package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/fs"
	"os"
	pathpkg "path"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

type graderConfig struct {
	RegexMatch    []string `yaml:"regex_match"`
	RegexNotMatch []string `yaml:"regex_not_match"`
}

type grader struct {
	Type   string       `yaml:"type"`
	Name   string       `yaml:"name"`
	Config graderConfig `yaml:"config"`
}

type task struct {
	ID      string   `yaml:"id"`
	Graders []grader `yaml:"graders"`
}

type regexRef struct {
	TaskID   string
	TaskPath string
	Path     string
	Grader   string
	List     string
	Index    int
	Pattern  string
	Regex    *regexp.Regexp
}

type contrastiveFile struct {
	Cases []contrastiveCase `json:"cases"`
}

type contrastiveCase struct {
	Name         string   `json:"name"`
	Task         string   `json:"task"`
	Grader       string   `json:"grader"`
	List         string   `json:"list"`
	Index        *int     `json:"index"`
	Matches      []string `json:"matches"`
	DoesNotMatch []string `json:"does_not_match"`
}

func taskPaths(root string) ([]string, error) {
	var paths []string
	err := filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() || filepath.Ext(path) != ".yaml" {
			return nil
		}
		relativePath, relativeErr := filepath.Rel(root, path)
		if relativeErr != nil {
			return relativeErr
		}
		parts := strings.Split(filepath.ToSlash(relativePath), "/")
		if len(parts) >= 2 && parts[len(parts)-2] == "tasks" {
			paths = append(paths, path)
		}
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Strings(paths)
	return paths, nil
}

func collect(root string) ([]regexRef, int, error) {
	paths, err := taskPaths(root)
	if err != nil {
		return nil, 0, err
	}
	if len(paths) == 0 {
		return nil, 0, fmt.Errorf("no task YAML files found under %s", root)
	}

	var refs []regexRef
	taskIDs := make(map[string]string)
	for _, path := range paths {
		relativePath, relativeErr := filepath.Rel(root, path)
		if relativeErr != nil {
			return nil, 0, relativeErr
		}
		displayPath := filepath.ToSlash(relativePath)
		data, readErr := os.ReadFile(path)
		if readErr != nil {
			return nil, 0, fmt.Errorf("%s: read task: %w", displayPath, readErr)
		}
		var value task
		if decodeErr := yaml.Unmarshal(data, &value); decodeErr != nil {
			return nil, 0, fmt.Errorf("%s: decode YAML: %w", displayPath, decodeErr)
		}
		if value.ID == "" {
			return nil, 0, fmt.Errorf("%s: task id is empty", displayPath)
		}
		suite := filepath.ToSlash(filepath.Dir(filepath.Dir(relativePath)))
		idKey := suite + "\x00" + value.ID
		if previous, exists := taskIDs[idKey]; exists {
			return nil, 0, fmt.Errorf("duplicate task id %s in suite %s: %s and %s", value.ID, suite, previous, displayPath)
		}
		taskIDs[idKey] = displayPath
		for _, grader := range value.Graders {
			if grader.Type != "text" {
				continue
			}
			lists := []struct {
				name     string
				patterns []string
			}{
				{name: "regex_match", patterns: grader.Config.RegexMatch},
				{name: "regex_not_match", patterns: grader.Config.RegexNotMatch},
			}
			for _, list := range lists {
				for index, pattern := range list.patterns {
					compiled, compileErr := regexp.Compile(pattern)
					if compileErr != nil {
						return nil, 0, fmt.Errorf("%s: task %s grader %s %s[%d]: %w", displayPath, value.ID, grader.Name, list.name, index, compileErr)
					}
					refs = append(refs, regexRef{TaskID: value.ID, TaskPath: displayPath, Path: displayPath, Grader: grader.Name, List: list.name, Index: index, Pattern: pattern, Regex: compiled})
				}
			}
		}
	}
	return refs, len(paths), nil
}

func refKey(taskPath, graderName, list string, index int) string {
	return fmt.Sprintf("%s\x00%s\x00%s\x00%d", taskPath, graderName, list, index)
}

func normalizeTaskPath(value string) string {
	return pathpkg.Clean(strings.ReplaceAll(value, `\`, "/"))
}

func validateCases(path string, refs []regexRef) (int, error) {
	if path == "" {
		return 0, nil
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return 0, err
	}
	var cases contrastiveFile
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&cases); err != nil {
		return 0, fmt.Errorf("%s: decode contrastive cases: %w", path, err)
	}
	if err := decoder.Decode(&struct{}{}); !errors.Is(err, io.EOF) {
		return 0, fmt.Errorf("%s: decode contrastive cases: expected one JSON document", path)
	}
	if len(cases.Cases) == 0 {
		return 0, fmt.Errorf("%s: cases must contain at least one contrastive case", path)
	}
	index := make(map[string]regexRef, len(refs))
	for _, ref := range refs {
		key := refKey(ref.TaskPath, ref.Grader, ref.List, ref.Index)
		if _, exists := index[key]; exists {
			return 0, fmt.Errorf("duplicate regex selector for task %s grader %s %s[%d]", ref.TaskPath, ref.Grader, ref.List, ref.Index)
		}
		index[key] = ref
	}
	for caseIndex, item := range cases.Cases {
		name := item.Name
		if name == "" {
			name = fmt.Sprintf("case %d", caseIndex)
		}
		if item.List != "regex_match" && item.List != "regex_not_match" {
			return 0, fmt.Errorf("%s: %s: list must be regex_match or regex_not_match", path, name)
		}
		if item.Index == nil {
			return 0, fmt.Errorf("%s: %s: index is required", path, name)
		}
		if len(item.Matches) == 0 || len(item.DoesNotMatch) == 0 {
			return 0, fmt.Errorf("%s: %s: matches and does_not_match must each contain at least one input", path, name)
		}
		taskPath := normalizeTaskPath(item.Task)
		selector := fmt.Sprintf("task %s grader %s %s[%d]", taskPath, item.Grader, item.List, *item.Index)
		ref, ok := index[refKey(taskPath, item.Grader, item.List, *item.Index)]
		if !ok {
			return 0, fmt.Errorf("%s: %s: regex selector not found: %s", path, name, selector)
		}
		for inputIndex, input := range item.Matches {
			if !ref.Regex.MatchString(input) {
				return 0, fmt.Errorf("%s: %s: matches[%d] did not match %s (task id %s, file %s)", path, name, inputIndex, selector, ref.TaskID, ref.TaskPath)
			}
		}
		for inputIndex, input := range item.DoesNotMatch {
			if ref.Regex.MatchString(input) {
				return 0, fmt.Errorf("%s: %s: does_not_match[%d] matched %s (task id %s, file %s)", path, name, inputIndex, selector, ref.TaskID, ref.TaskPath)
			}
		}
	}
	return len(cases.Cases), nil
}

func run(arguments []string, stdout, stderr io.Writer) error {
	flags := flag.NewFlagSet("go-regex-runner", flag.ContinueOnError)
	flags.SetOutput(stderr)
	root := flags.String("root", "", "evals or suite root containing tasks/*.yaml")
	cases := flags.String("cases", "", "optional JSON contrastive-case file")
	if err := flags.Parse(arguments); err != nil {
		return err
	}
	if *root == "" {
		return errors.New("--root is required")
	}
	refs, tasks, err := collect(*root)
	if err != nil {
		return err
	}
	caseCount, err := validateCases(*cases, refs)
	if err != nil {
		return err
	}
	fmt.Fprintf(stdout, "validated %d regexes across %d task files", len(refs), tasks)
	if *cases != "" {
		fmt.Fprintf(stdout, " and %d contrastive cases", caseCount)
	}
	fmt.Fprintln(stdout)
	return nil
}

func main() {
	if err := run(os.Args[1:], os.Stdout, os.Stderr); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

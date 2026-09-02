package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeTask(t *testing.T, root, pattern string) string {
	t.Helper()
	directory := filepath.Join(root, "sample", "tasks")
	if err := os.MkdirAll(directory, 0o755); err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(directory, "task.yaml")
	content := "id: sample-task\ngraders:\n  - type: text\n    name: task_completion\n    config:\n      regex_match:\n        - '" + pattern + "'\n      regex_not_match:\n        - 'forbidden'\n"
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	return path
}

func writeFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestCollectCompilesDecodedRegexes(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `(?m)^ok\s+value$`)
	refs, tasks, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	if tasks != 1 || len(refs) != 2 {
		t.Fatalf("got %d tasks and %d regexes", tasks, len(refs))
	}
	if refs[0].Pattern != `(?m)^ok\s+value$` {
		t.Fatalf("pattern was not decoded as expected: %q", refs[0].Pattern)
	}
	if !refs[0].Regex.MatchString("ok value") || refs[0].Regex.MatchString("okvalue") {
		t.Fatal("decoded regex does not have the expected whitespace behavior")
	}
}

func TestCollectRejectsEmptyRoot(t *testing.T) {
	_, _, err := collect(t.TempDir())
	if err == nil || !strings.Contains(err.Error(), "no task YAML files") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestTaskPathsUsePathsRelativeToRoot(t *testing.T) {
	root := filepath.Join(t.TempDir(), "tasks", "root")
	writeFile(t, filepath.Join(root, "eval.yaml"), "name: not-a-task\n")
	taskPath := writeTask(t, root, `^ok$`)
	paths, err := taskPaths(root)
	if err != nil {
		t.Fatal(err)
	}
	if len(paths) != 1 || paths[0] != taskPath {
		t.Fatalf("unexpected task paths: %v", paths)
	}
}

func TestCollectRejectsDuplicateIDsWithinSuite(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	second := filepath.Join(root, "sample", "tasks", "other.yaml")
	writeFile(t, second, "id: sample-task\ngraders: []\n")
	_, _, err := collect(root)
	if err == nil || !strings.Contains(err.Error(), "duplicate task id") || !strings.Contains(err.Error(), "sample/tasks/task.yaml") || !strings.Contains(err.Error(), "sample/tasks/other.yaml") || strings.Contains(err.Error(), root) {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestCollectAllowsDuplicateIDsAcrossSuites(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	writeFile(t, filepath.Join(root, "other", "tasks", "task.yaml"), "id: sample-task\ngraders: []\n")
	if _, tasks, err := collect(root); err != nil || tasks != 2 {
		t.Fatalf("got %d tasks, error %v", tasks, err)
	}
}

func TestCollectReportsRegexLocation(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `(`)
	_, _, err := collect(root)
	if err == nil {
		t.Fatal("expected invalid regex to fail")
	}
	for _, expected := range []string{"sample/tasks/task.yaml", "sample-task", "task_completion", "regex_match[0]"} {
		if !strings.Contains(err.Error(), expected) {
			t.Fatalf("error %q does not contain %q", err, expected)
		}
	}
}

func TestCollectReportsRegexNotMatchLocation(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "sample", "tasks", "task.yaml")
	writeFile(t, path, "id: sample-task\ngraders:\n  - type: text\n    name: completion\n    config:\n      regex_not_match:\n        - '('\n")
	_, _, err := collect(root)
	if err == nil || !strings.Contains(err.Error(), "regex_not_match[0]") || !strings.Contains(err.Error(), "sample/tasks/task.yaml") || strings.Contains(err.Error(), root) {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestCollectReportsMalformedYAMLAndMissingID(t *testing.T) {
	root := t.TempDir()
	bad := filepath.Join(root, "bad", "tasks", "task.yaml")
	writeFile(t, bad, "id: [\n")
	if _, _, err := collect(root); err == nil || !strings.Contains(err.Error(), "decode YAML") {
		t.Fatalf("unexpected YAML error: %v", err)
	}
	if err := os.RemoveAll(filepath.Join(root, "bad")); err != nil {
		t.Fatal(err)
	}
	missing := filepath.Join(root, "missing", "tasks", "task.yaml")
	writeFile(t, missing, "graders: []\n")
	if _, _, err := collect(root); err == nil || !strings.Contains(err.Error(), "task id is empty") {
		t.Fatalf("unexpected missing-id error: %v", err)
	}
}

func TestValidateCases(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	refs, _, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	casePath := filepath.Join(root, "cases.json")
	content := `{"cases":[{"name":"basic","task":"sample/tasks/task.yaml","grader":"task_completion","list":"regex_match","index":0,"matches":["ok"],"does_not_match":["no"]}]}`
	if err := os.WriteFile(casePath, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	count, err := validateCases(casePath, refs)
	if err != nil {
		t.Fatal(err)
	}
	if count != 1 {
		t.Fatalf("got %d cases", count)
	}
}

func TestValidateCasesNormalizesTaskPath(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	refs, _, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	casePath := filepath.Join(root, "cases.json")
	content := `{"cases":[{"name":"dot path","task":"./sample/tasks/task.yaml","grader":"task_completion","list":"regex_match","index":0,"matches":["ok"],"does_not_match":["no"]},{"name":"Windows path","task":"sample\\tasks\\task.yaml","grader":"task_completion","list":"regex_match","index":0,"matches":["ok"],"does_not_match":["no"]}]}`
	writeFile(t, casePath, content)
	count, err := validateCases(casePath, refs)
	if err != nil {
		t.Fatal(err)
	}
	if count != 2 {
		t.Fatalf("got %d cases", count)
	}
}

func TestValidateCasesReportsMismatch(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	refs, _, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	casePath := filepath.Join(root, "cases.json")
	content := `{"cases":[{"name":"bad expectation","task":"sample/tasks/task.yaml","grader":"task_completion","list":"regex_match","index":0,"matches":["no"],"does_not_match":["other"]}]}`
	if err := os.WriteFile(casePath, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	_, err = validateCases(casePath, refs)
	if err == nil || !strings.Contains(err.Error(), "matches[0] did not match") || !strings.Contains(err.Error(), "sample/tasks/task.yaml") || !strings.Contains(err.Error(), "task_completion regex_match[0]") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestValidateCasesRejectsInvalidContracts(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	refs, _, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	tests := []struct {
		name    string
		content string
		want    string
	}{
		{name: "malformed JSON", content: `{`, want: "decode contrastive cases"},
		{name: "missing cases", content: `{}`, want: "at least one contrastive case"},
		{name: "empty cases", content: `{"cases":[]}`, want: "at least one contrastive case"},
		{name: "unknown field", content: `{"case":[]}`, want: "unknown field"},
		{name: "multiple documents", content: `{"cases":[]} {"cases":[]}`, want: "expected one JSON document"},
		{name: "invalid list", content: `{"cases":[{"name":"bad","task":"sample/tasks/task.yaml","grader":"task_completion","list":"other","index":0,"matches":["ok"],"does_not_match":["no"]}]}`, want: "list must be"},
		{name: "missing index", content: `{"cases":[{"name":"bad","task":"sample/tasks/task.yaml","grader":"task_completion","list":"regex_match","matches":["ok"],"does_not_match":["no"]}]}`, want: "index is required"},
		{name: "vacuous", content: `{"cases":[{"name":"bad","task":"sample/tasks/task.yaml","grader":"task_completion","list":"regex_match","index":0}]}`, want: "must each contain"},
		{name: "missing selector", content: `{"cases":[{"name":"bad","task":"missing/tasks/task.yaml","grader":"task_completion","list":"regex_match","index":0,"matches":["ok"],"does_not_match":["no"]}]}`, want: "missing/tasks/task.yaml"},
		{name: "negative mismatch", content: `{"cases":[{"name":"bad","task":"sample/tasks/task.yaml","grader":"task_completion","list":"regex_match","index":0,"matches":["ok"],"does_not_match":["ok"]}]}`, want: "does_not_match[0]"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			path := filepath.Join(root, strings.ReplaceAll(test.name, " ", "_")+".json")
			writeFile(t, path, test.content)
			_, err := validateCases(path, refs)
			if err == nil || !strings.Contains(err.Error(), test.want) {
				t.Fatalf("error %v does not contain %q", err, test.want)
			}
		})
	}
}

func TestValidateCasesRejectsDuplicateSelectors(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "sample", "tasks", "task.yaml")
	writeFile(t, path, "id: sample-task\ngraders:\n  - type: text\n    name: duplicate\n    config:\n      regex_match: ['^one$']\n  - type: text\n    name: duplicate\n    config:\n      regex_match: ['^two$']\n")
	refs, _, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	casePath := filepath.Join(root, "cases.json")
	writeFile(t, casePath, `{"cases":[{"task":"sample/tasks/task.yaml","grader":"duplicate","list":"regex_match","index":0,"matches":["one"],"does_not_match":["no"]}]}`)
	_, err = validateCases(casePath, refs)
	if err == nil || !strings.Contains(err.Error(), "duplicate regex selector") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestValidateCasesTargetsRegexNotMatch(t *testing.T) {
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	refs, _, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(root, "cases.json")
	writeFile(t, path, `{"cases":[{"task":"sample/tasks/task.yaml","grader":"task_completion","list":"regex_not_match","index":0,"matches":["forbidden"],"does_not_match":["allowed"]}]}`)
	if _, err := validateCases(path, refs); err != nil {
		t.Fatal(err)
	}
}

func TestCollectIgnoresRegexFieldsOnNonTextGraders(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "sample", "tasks", "task.yaml")
	writeFile(t, path, "id: sample-task\ngraders:\n  - type: prompt\n    name: judge\n    config:\n      regex_match: ['(']\n")
	refs, tasks, err := collect(root)
	if err != nil {
		t.Fatal(err)
	}
	if tasks != 1 || len(refs) != 0 {
		t.Fatalf("got %d tasks and %d regexes", tasks, len(refs))
	}
}

func TestRunRequiresRootAndReportsCounts(t *testing.T) {
	var stdout, stderr bytes.Buffer
	if err := run(nil, &stdout, &stderr); err == nil || !strings.Contains(err.Error(), "--root is required") {
		t.Fatalf("unexpected error: %v", err)
	}
	root := t.TempDir()
	writeTask(t, root, `^ok$`)
	stdout.Reset()
	if err := run([]string{"--root", root}, &stdout, &stderr); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(stdout.String(), "validated 2 regexes across 1 task files") {
		t.Fatalf("unexpected output: %q", stdout.String())
	}
	casePath := filepath.Join(root, "cases.json")
	writeFile(t, casePath, `{"cases":[{"task":"sample/tasks/task.yaml","grader":"task_completion","list":"regex_match","index":0,"matches":["ok"],"does_not_match":["no"]}]}`)
	stdout.Reset()
	if err := run([]string{"--root", root, "--cases", casePath}, &stdout, &stderr); err != nil {
		t.Fatal(err)
	}
	if stdout.String() != "validated 2 regexes across 1 task files and 1 contrastive cases\n" {
		t.Fatalf("unexpected cases output: %q", stdout.String())
	}
}

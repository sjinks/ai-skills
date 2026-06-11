# Language Appendix: Cross-Language API Equivalents

Read this when mapping checklist gates to concrete APIs in Node/TypeScript, Python, Go, Rust, C, C++, or Windows (Win32/.NET).


| Concern | Node / TypeScript | Python | Go | Rust | C | C++ | Windows (Win32 / .NET) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonicalize root | `fs.realpathSync` / `fs.promises.realpath` | `os.path.realpath` | `filepath.EvalSymlinks` | `std::fs::canonicalize` | `realpath(3)` | `std::filesystem::canonical` | `GetFinalPathNameByHandle` / `Path.GetFullPath` |
| `lstat` (no follow) | `fs.lstatSync` / `fs.promises.lstat` | `os.lstat` | `os.Lstat` | `std::fs::symlink_metadata` | `lstat(2)` | `::lstat` (POSIX) / `std::filesystem::symlink_status` | `GetFileAttributesExW` (check `FILE_ATTRIBUTE_REPARSE_POINT`) / `File.GetAttributes` |
| Symlink check | `stats.isSymbolicLink()` | `stat.S_ISLNK(st_mode)` | `mode & fs.ModeSymlink != 0` | `metadata.file_type().is_symlink()` | `S_ISLNK(st.st_mode)` | `std::filesystem::is_symlink(std::filesystem::symlink_status(p))` | `attr & FILE_ATTRIBUTE_REPARSE_POINT != 0` |
| Directory check | `stats.isDirectory()` | `stat.S_ISDIR(st_mode)` | `info.IsDir()` | `metadata.is_dir()` | `S_ISDIR(st.st_mode)` | `std::filesystem::is_directory(std::filesystem::symlink_status(p))` | `attr & FILE_ATTRIBUTE_DIRECTORY != 0` |
| Open without follow | `fs.openSync(p, fs.constants.O_RDWR \| fs.constants.O_NOFOLLOW)` | `os.open(..., os.O_NOFOLLOW)` | `unix.O_NOFOLLOW` | `OpenOptions::custom_flags(libc::O_NOFOLLOW)` | `open(path, flags \| O_NOFOLLOW, mode)` | `::open(path.c_str(), flags \| O_NOFOLLOW, mode)` | `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT` |
| Non-recursive mkdir | `fs.mkdirSync(p)` (no `recursive`) | `os.mkdir(p)` | `os.Mkdir(p, mode)` | `std::fs::create_dir(p)` | `mkdir(path, mode)` | `std::filesystem::create_directory` | `CreateDirectoryW` |
| Per-job temp dir | `fs.mkdtempSync(prefix)` | `tempfile.mkdtemp(prefix=)` | `os.MkdirTemp(dir, prefix)` | `tempfile::TempDir::new_in` | `mkdtemp(template)` | `mkdtemp` via wrapper / `std::filesystem::temp_directory_path` + unique suffix | `GetTempPathW` + `CreateDirectoryW` with unique suffix |
| Anchor-relative ops | n/a (no `*at` in stdlib) | `os.open(..., dir_fd=fd)`, `os.mkdir(..., dir_fd=fd)`, `os.unlink(..., dir_fd=fd)` (see `os.supports_dir_fd`) | `unix.Openat`, `unix.Mkdirat`, `unix.Unlinkat` | `openat` crate | `openat`, `mkdirat`, `unlinkat` | `::openat`, `::mkdirat`, `::unlinkat` | n/a (no `*at` family on Win32) |


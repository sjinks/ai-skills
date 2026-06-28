# Allocation-counting `LD_PRELOAD` shim

Read this when you need the `mallocount` skeleton referenced from Core Principle 2
of `SKILL.md` — the C source, the build invocation, and the `dlsym` bootstrap
gotchas. The skeleton below is intentionally minimal: it counts `malloc` only and
is *not* copy/paste-ready. A robust shim needs the `dlsym` re-entrancy guard and
the `calloc`/`realloc`/`free` handling described under "Gotchas" before it is safe
to run.

An `LD_PRELOAD` shim that overrides `malloc`/`calloc`/`realloc` and prints a total
at exit gives an exact allocation count for a fixed workload — no profiler, no
sampling error. Once you have extended the minimal skeleton with the Gotchas
handling below (the `dlsym` re-entrancy guard and `calloc`/`realloc`/`free`
cases), build it and run the target under it — do **not** run the bare skeleton as
shown, it can recurse during `dlsym` resolution:

```sh
# build the COMPLETED shim (mallocount.c here is your finished file, not the
# minimal skeleton printed below)
gcc -O2 -shared -fPIC -o mallocount.so mallocount.c -ldl
LD_PRELOAD=./mallocount.so <server>
```

Minimal skeleton (`mallocount.c`):

```c
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdio.h>
static atomic_ullong n;
static void *(*real_malloc)(size_t);
void *malloc(size_t s){
  if(!real_malloc) real_malloc=(void *(*)(size_t))dlsym(RTLD_NEXT,"malloc");
  atomic_fetch_add(&n,1); return real_malloc(s); }
__attribute__((destructor)) static void rep(void){
  unsigned long long total = atomic_load(&n);
  fprintf(stderr,"allocs=%llu\n",total); }
```

Gotchas when extending it to `calloc`/`realloc`:

- `dlsym()` itself can allocate (via `malloc` or `calloc`) during the first
  resolution, when `real_malloc`/`real_calloc` is still `NULL` — a naive hook
  recurses. Gate re-entry with a thread-safe "resolving" flag, or serve those
  bootstrap allocations from a small static arena until the real symbol resolves.
- Apply the same arena guard to `calloc`.
- Make `free()` recognise and ignore bootstrap-arena pointers so it never passes
  them to the real `free`.
- Cast every `dlsym` result to the matching function-pointer type; assigning the
  raw `void *` is undefined in ISO C and fails under `-Werror`.

Isolate the **per-request** figure by differencing two fixed request counts over
one keep-alive connection: `per_request = (allocs@N2 − allocs@N1) / (N2 − N1)`.
The subtraction cancels process startup and first-request warm-up.

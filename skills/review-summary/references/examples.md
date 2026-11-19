Read this reference for examples of acknowledging an author’s work while making the review decision clear.

## Request changes

The reviewer likes that local and remote files share one listing interface. The review requests two fixes and includes an inline comment for each with a suggested fix and check.

> Thanks for working on this. I like that callers can list local and remote files through the same interface. I found two cases I’d like us to fix before merging.
>
> 1. When removing a local directory and its contents, the cleanup code could delete a remote file the caller didn’t ask it to remove.
> 2. Trying to open a local directory that doesn’t exist could create it.
>
> I’ve left an inline comment on each case with a suggested fix and a way to check it.

## Approve after a fix

The author fixed both issues. The reviewer checked both behaviors and approved the changes.

> Thanks for fixing both cases. I checked that cleanup stays local and that opening a missing directory fails without creating it. This looks good to merge.

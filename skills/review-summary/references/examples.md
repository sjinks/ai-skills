Read this reference for examples of acknowledging an author’s work while making the review decision clear.

## Request changes

The reviewer likes that local and remote files share one listing interface. The review requests two fixes and includes an inline comment for each with a suggested fix and check.

> Thanks for giving callers one way to list both local and remote files. I found two cases I’d like us to fix before merging.
>
> 1. When removing a local directory and its contents, the cleanup code could delete a remote file the caller didn’t ask it to remove.
> 2. Trying to open a local directory that doesn’t exist could create it.
>
> I’ve left an inline comment on each case with a suggested fix and a way to check it.

## Request changes when the strength is in the PR description

The PR description says that a background job and an API route now share one query. The reviewer’s notes mention only that the new query excludes launched sites without the WordPress initialization marker.

> I like that the job and the API route now share one query. Before merging, please keep launched sites eligible for monitoring even when they don’t have the WordPress initialization marker. Otherwise, those sites could miss uptime monitoring.

## Approve after a fix

The author fixed both issues. The reviewer checked both behaviors and approved the changes.

> Thanks for keeping cleanup local and making sure that opening a missing directory fails without creating it. I checked both cases, and this looks good to merge.

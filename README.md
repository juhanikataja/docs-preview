# hacky docs previewwer

## Env vars

* `WORKPATH` where git repository is cloned
* `BUILDROOT` where builds are stored. This directory should be shared with HTTP static content server.
* `BUILDSECRET` secret key for triggering builds at `/build/<secret>`.
  * This must be set

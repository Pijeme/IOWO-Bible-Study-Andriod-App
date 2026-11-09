# Website connection for IOWO D4 Bible Study

The module was integrated into the website source on 9 November 2026 in commit
`a693a49`. GitHub and Docker image `pijeme/district4-tool-main:20261109-a693a49`
(also `latest` and `main`) contain it. The local website endpoint responds
correctly. The latest public endpoint check now returns the expected HTTP 400
username/password validation response to an empty JSON request. The live
mobile-login connection is reachable. The update instructions below remain
available for other servers or deployments that still return HTTP 404.

The current website/Drive backup was confirmed complete before this source
update. On the live server, keep the existing Compose project/data volume, set
any pinned `IMAGE_TAG` to `20261109-a693a49` (or `latest`), then run:

```text
docker compose pull district4
docker compose up -d --no-deps district4
```

Do not remove volumes. No `.env` secrets or existing notes need to be replaced.
An empty JSON POST to `/api/v1/bible-mobile/login` should then return HTTP 400
with a username/password validation message, instead of HTTP 404. The desktop
preview can retry its existing login screen once this server update is active.

The following manual source-install instructions are retained for deployments
which do not use the published website image:

After the current website/Drive backup has completed:

1. Copy `mobile_bible_api.py` beside the website's `app.py`.
2. After `register_bible_study_routes(app)` in `app.py`, add:

   ```python
   from mobile_bible_api import register_mobile_bible_routes
   register_mobile_bible_routes(app)
   ```

3. Keep the existing server-only `SERMON_NOTES_DRIVE_SCRIPT_URL`, `SERMON_NOTES_DRIVE_API_TOKEN`, Google credentials and stable `FLASK_SECRET_KEY`. Do not copy them into the Android project.
4. Publish/restart the website using its usual deployment workflow after the backup finishes. No Apps Script redeployment is required for this module.
5. The app signs in through `https://iowod4tool.coresite.pro/api/v1/bible-mobile/login`. Subsequent requests use a revocable device token. The password is not retained on the phone.

Device authorization records are stored in `mobile_devices.db` beside the server's personal sermon-note database. Keep that file in the server's private data volume. It contains token hashes rather than raw tokens. Password changes or account removal invalidate online device authorization after the website's account cache refreshes; the phone's existing offline reading remains available.

The bridge authenticates the existing Sheets-backed account cache. Mobile note synchronization waits for the website's current sync, exchanges notes with Drive, and refreshes the website again. Each request is restricted to the authenticated account. Developer-only conversion remains developer-only and uses the website's private sermon source collection.

Avoid simultaneous manual backups from separate website instances for the same account. An already-running job in this website process is reused rather than duplicated. Existing Google Drive and local notes remain authoritative; the Android installation contains public study resources only.

The registration line is the only required change to the website. Review this file and the supplied tests before deploying it. Do not enable it while the current bulk backup is running.

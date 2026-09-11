# Supporting-page sharing metadata

The local methodology page rendered the homepage Open Graph title, “Know the game. Respect the uncertainty.”, and no canonical URL. The same root metadata supplied generic sharing text to other supporting pages.

A shared metadata helper now provides page-specific titles, descriptions, canonical URLs, Open Graph URLs and the existing site image for ratings, methodology, performance, about, privacy, contact and responsible use. Ratings sort variants retain `/ratings` as their canonical URL. The privacy description explains its actual subject instead of using the update-date introduction. Unknown article slugs retain not-found behavior and no-index metadata.

Chromium and WebKit verified all seven routes, including the offense-sorted ratings URL (14 checks). Each rendered a distinct title, matching description/Open Graph description, expected canonical/OG URL and an image. Evidence is `editorial-metadata-browser.json`. The production build passed.

This improves the accuracy of the site's emitted sharing metadata. It does not establish how third-party crawlers will cache previews or imply improved search ranking. The updated pages are staged locally/GitHub; public deployment remains pending.

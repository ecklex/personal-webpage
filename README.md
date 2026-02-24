# personal-webpage

Personal website and CV for Alexander Eckerlin, built with [Jekyll](https://jekyllrb.com/) and hosted on [GitHub Pages](https://pages.github.com/).

🔗 **Live site:** [ecklex.github.io](https://ecklex.github.io)

## Tech Stack

- **Generator:** Jekyll (via GitHub Pages)
- **Theme:** [Cayman](https://github.com/pages-themes/cayman) (`pages-themes/cayman@v0.2.0`)
- **Hosting:** GitHub Pages

## Local Development

1. Install [Ruby](https://www.ruby-lang.org/) and [Bundler](https://bundler.io/).
2. Create a `Gemfile` (if not already present):
   ```ruby
   source "https://rubygems.org"
   gem "github-pages", group: :jekyll_plugins
   ```
3. Install dependencies:
   ```bash
   bundle install
   ```
4. Serve locally:
   ```bash
   bundle exec jekyll serve
   ```
5. Open `http://localhost:4000` in your browser.

## Deployment

Any push to the `main` branch is automatically deployed to GitHub Pages.

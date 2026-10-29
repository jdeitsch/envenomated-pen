# ePub Data Poisoning Injector 🛡️



A lightweight utility designed to help authors and creators inject custom text, markup, or data-poisoning payloads into random paragraphs of their ePub files. This helps disrupt unauthorized text scraping and LLM training on copyrighted works.



## Features

- **Simple Graphical Interface (GUI):** No command line required for end users.

- **Randomized Injection:** Seamlessly embeds your payload (`poison.txt`) between random `<p>` tags within the book's internal XHTML files.
> _Note:_ Your poison text will need to be HTML encoded to make it not render in the final eBook file. See the `poison.EXAMPLE.txt` for the correct formatting 

- **Cross-Platform:** Works on both Windows and macOS.



## For Non-Technical Users (Ready-to-use App)

1. Download the latest `.exe` (Windows) from the **Releases** tab on this GitHub repository.

2. Double-click the application.

3. Select your `.epub` file and your text/HTML payload file.

4. Click **Inject and Save ePub**.



## For Developers (Running from Source)

1. Clone the repository:

```bash
git clone https://github.com/jdeitsch/epub-poison-injector.git
cd epub-poison-injector
```

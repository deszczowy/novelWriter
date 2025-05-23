# novelWriter Internationalisation (i18n)

The maintenance of translations has been moved to the Crowdin service. The translation strings can
be edited there at the [novelWriter project page](https://crowdin.com/project/novelwriter).
However, please read the Translation Guidelines section below.

You can still use the manual approach listed below, and then upload the file through the website's
interface. The translation strings for that language will then be updated and queued for approval.

To verify a language file translated through the Crowdin tool, download and extract it into the
`i18n` folder in the novelWriter source and follow the instructions in
[Generate an Updated Translation File](#generate-an-updated-translation-file) below.


# Translation Guidelines

When contributing translations, keep the following things in mind.

* For descriptive labels and dialog boxes, make sure you do _not_ change the meaning of the text
  when you translate it from English. The user must receive the same instructions or information
  regardless of language. This is important, otherwise the documentation will be inconsistent with
  the user interface and it will become a lot more difficult to handle user issues and questions.
* If you think a label or description is misleading or incomplete, please file an issue report. The
  correct way to handle such changes is to change the text in the code first, which will then be
  forwarded to _all_ translators such that the GUI is consistent across all languages.
* For very short labels, like button labels. it may be fine to replace the word with a similar
  word, but only as long as the user understands what it is supposed to do. Some buttons and tabs
  have limited space. If necessary, it is OK to use abbreviations.


# Direct Approach Using Qt Linguist

Here you will find instructions for translating novelWriter to a new language directly using Qt
Linguist, or updating the translations for an already existing supported language.

There are two areas relevant to localisation:

* The Qt GUI translation files, which consists of `nw_XX.ts` files. This is the bulk of the
  translation work.
* The `project_XX.json` files. See [Project Localisation](#project-localisation) below.

The `XX` in the file name corresponds to the language and country code for the translation. For
instance `en_GB` for British English.


## Qt GUI Localisation

You will need the translation tool Qt Linguist on your system.

For Ubuntu/Debian, run:

```bash
sudo apt install qttools5-dev-tools
```

See also [Qt Linguist Manual: Translators](https://doc.qt.io/qt-6/linguist-translators.html).


### Workflow

Here's an overview of the localisation workflow:

1. First, create a new branch off of `main`, and there, generate a new `nw_XX.ts` translation file.
1. Load the translation file in Qt Linguist. Translate and save your changes.
1. Generate the `nw_XX.qm` file.
1. Run the application and verify your changes. Iterate from step 2.
1. Once finished, commit your changes and submit your pull request.

When you want to translate new changes, again create a new branch off of `main` and re-generate the
translation file. Continue from step 2.


### Generate an Updated Translation File

The `i18n` folder at the root of the repository contains the `nw_XX.ts` translation files.

Whether to add a new language to the translation framework, or to  update the file against the
current source code, you must first run the `qtlupdate` command:

```bash
python3 pkgutils.py qtlupdate i18n/nw_XX.ts
```

The file name must be in the correct format. All translation files must be located in the `i18n`
folder, start with `nw_` and end with `.ts`. In between goes the language and country code. It must
be a valid ISO language code, otherwise novelWriter will not accept the file.

For instance, the French translation uses the language code `fr_FR`, so its translation file will
be `nw_fr_FR.ts`

Note: The `qtlupdate` command needs the `lupdate` tool provided by PyQt6, which uses the latest
TS file format. On Debian/Ubuntu it is provided by the package `pyqt6-dev-tools`.


### Edit the Translation File in Qt Linguist

The `i18n/nw_XX.ts` file can be edited with the Qt Linguist application provided by Qt. This is
by far easier than manually editing the `.ts` file.

Please select "English" and "United Kingdom" as the _source_ language if prompted by Qt Linguist.


### Verify Your Translation

The application does not use `.ts` files directly. The `novelwriter/assets/i18n/nw_XX.qm` files are
the actual files used to translate the GUI into another language other than the default British
English. These files are not generated by default, but they can be built with:

```bash
python3 pkgutils.py qtlrelease
```

You can now test the translation in novelWriter. The Preferences dialog should list the newly added
language, so go ahead and select it.


### Missing QtBase Translations

The default Qt dialogs also have translations, for instance for standard buttons like "Yes", "No",
"Ok", "Cancel", etc. Generally, these translation files are installed with the Qt libraries on your
system, and novelWriter will collect those translations from there. However, these translations are
missing for many languages.

As a starting point, there is no need to translate any entries in the `.ts` files that are under
elements starting with the letter "Q", like "QPlatformTheme", "QWizard", etc. If these turn up in
English in novelWriter after activating a translation, it means they are probably missing in the Qt
library, and you may also need to translate these.

These additional translation entries are generated from a file named `i18n/qtbase.py`, which is not
a file that novelWriter uses. It is there only to generate these additional entries for the `.ts`
files.


## Project Localisation

Projects can have a different language setting than the GUI itself. The files with format
`project_XX.json` in `novelwriter/assets/i18n` are simple translation maps for text that goes into
the exported documents generated by the Build Novel Project tool.

The files are loaded based on the language setting in the Build Novel Project tool. At the present
time, no other parts of the application use these files. Since these are used as replacement
lookups, they are maintained as plain JSON files. The main usage is to generate chapter headers as
number words.

Adding new translations for these files is easy. Just copy the `project_en_GB.json` file, rename it
to the appropriate language coded filename, and open it in a text editor and edit the content.

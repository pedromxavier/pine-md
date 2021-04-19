# Pine Markdown
### _An acid markdown flavour_



<br>
<br>

# Install & Quick Start
```shell
$ pip install pine-md
$ pine --help
```
## For Linux:
```bash
$ pine source.md > index.html
```
## For MacOS:
```bash
$ python -m pine source.md > index.html
```
## For Windows (UTF-8 issues involved):
```shell
> pine source.md -o index.html
```

# Introduction
This is _Pine Markdown_, or simply, _pine-md_. The greatest motivation behind the development of this _acid_, _spicy_ and _exotically delicious_ markdown flavour came from a few issues felt on other document specification languages. Yes, it is about keeping it simple, but we want some of our power back.

# Cheatsheet

## Simple HTML Documents
```mathematica
html
$   title = "Home"
$   author = "Pine"
$   year = "MMXXI"
head
/   "head.md"
    [./static/css/style.css]@css
    [./static/js/script.js]@js
body
    {   .center
        Here you may write whatever you want. Special characters are amazing:
        `code`, _italic_, *bold*, ~strikethrough~ and \(maybe\) more.
        Yes, some things must be escaped, for good reasons.
        We have [https://somelink.net](links)! Want to open on a new tab?
        Try those: [https://newtablink.net]@(link).
    }
    {   #incredible .fancy .box-sized
        After applying id and classes to your div you might want to include an image:
        [./static/images/cat.jpg]@img
        There it goes.
    }
    {   .reasons
        Reasons to use pine-md:
        - Reason #1: We use LALR\(1\) parsers:  No \(severe\) ambiguity on this grammar!
        - Reason #2: You can just type in your regular html, as always.
        - Reason #3: See by yourself next.
    }
/   "./src/extra_source.md"
    {   #greatest-reason
        See? Another bunch of pine code was suddenly included! No more need to copy and paste your good ol' footers, headers and navs around.
        Once more:
    }
/   "./src/footer.md"
    {   p
        In this last paragraph, lets talk about the year of $year: In fact, no good words about it...
    }
```

_**Disclaimer:** Unfortunately this README.md document wasn't rendered with pine-md. Yet!_
!   x. Some brief Comment
!   This is the main page from the Pine-MD Project. Rendered via Pine-MD.

!   x. First, testing variable assignment via JS

    §§
        var title = "Pine-MD";
        var year = 2021;
    §§

!   Testing HTML divs and variable evaluation
    { html
        { head
            { title
            §title§
            }
            [./static/css/style.css]@css
            [./static/js/script.js]@js
        }
        { body
!           Include navbar
            [./nav.mp]@mp
!           Testing Headers and text
            { .content
                { #intro
                    #1 Introduction
                    This the official page for Pine-MD, _an acid Markdown flavor_.
                }
                { #about
                    #1 About
                    Pine-MD is intended to be an alternative, more powerful, still simple, Markdown Syntax.

                    #2 Installation
                    Installing Pine-MD is very simple.

                    #3 Linux
                    ```bash
                    $ pip install pine-md
                    ```

                    #3 Windows
                    ```shell
                    > python -m pip install pine-md
                    ```
                }
                { #usage
                    #1 Usage

                    #2 Basic Use
                    Pine-MD is mostly served through its command-line interface.

                    ```bash
                    $ pine --help
                    ```

                    A pine file ((extension `.mp`))
                    Now, some [#](link), or some [#]*(new tab link).
                    Last, but not least, include a picture.
                    { profile
                        [./static/assets/pine-md.png]@img
                    }
                }
!               Testing some common div and lists
                {
                    This is a simple div. Now, some lists
                    - First, this.
                    - Second, that.
                    - Third, this one.
                    - Last, the fourth
                        + The fifth
                        + The fifth again
                    - Back to the seventh
                    Ok, the list just ended
                }
            }
!           Testing some div and variable evaluation
            [./footer.mp]@mp
        }
    }
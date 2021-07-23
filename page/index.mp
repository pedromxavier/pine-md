#   0. Some brief Comment
#   This is the main page from the Pine-MD Project. Rendered via Pine-MD.

#   1. First, testing variable assignment via JS

    §
        var title = "Pine-MD";
        var year = 2021;
    §

#   2. Testing plain HTML and variable evaluation
    { html
    { head
        { title
        §title§
        }
    }
    { body
#   3. Test false include
#   Should display Warning.
    [./folder/file.mp]@mp

#   4. Now, some real include
    [./INCLUDEME.mp]@mp
    
#   5. Testing Headers and text
    #1 Introduction
    This is Pine-MD's official page, an acid _Markdown_ flavor.

    #2 Installation.
    Installing Pine-MD is very simple.

    #3 Linux
    `$ pip install pine-md`

    #3 Windows
    `> python -m pip install pine-md`

#   6. Testing some common div and lists
    {
        This is a simple div. Now, some lists
        - First, this.
        - Second, that.
        - Third, this one.
        - Last, the fourth
        Ok, the list just ended
    }

#   7. Testing some div and variable evaluation
    {   footer #unique .main.ultra.fashion
        Rio de Janeiro &copy; §year§
    }
    }
    }
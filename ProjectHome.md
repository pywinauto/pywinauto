Gui Automation with Python

_If you use pywinauto - or you want to get started - then I think SWAPY
http://code.google.com/p/swapy/ is a VERY interesting tool. I have only looked at the video - but that alone convinced me to post a link to it. **VERY COOL**_

![http://wiki.pywinauto.googlecode.com/hg/notepad-simple2-ir.gif](http://wiki.pywinauto.googlecode.com/hg/notepad-simple2-ir.gif)


It is simple and the resulting scripts are very readable. How simple?
```
app.Notepad.MenuSelect("Help->About Notepad")
app.AboutNotepad.OK.Click()
app.Notepad.Edit.TypeKeys ("pywinauto Works!", with_spaces = True)
```

Please see the documentation at: http://pywinauto.googlecode.com/hg/pywinauto/docs/index.html




**Note:** if searching for pywinauto - then you may find links to:
  * http://pywinauto.pbworks.com/ - Old wiki - really want to move into docs or here
  * https://sourceforge.net/projects/pywinauto
  * https://lists.sourceforge.net/lists/listinfo/pywinauto-users - Mailing List (best way to get help)
  * Blog (not updated often) http://pywinauto.blogspot.com/
  * http://pywinauto.openqa.org/ - Old links may point here (forum and bugs used to be there - but this site is not used anymore)

I am trying to consolidate most information to this site.
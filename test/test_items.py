from pine.items import mdHTML, mdHead, mdBody
from pine.items import mdText, mdHTML, mdBody, mdHead, mdHeader, mdDiv, mdBold

md = mdHTML(
    mdHead(
        mdText('<title>Pine-md Test Page</title>')
    ),

    mdBody(
        mdHeader.new(1)(mdText('Test some header')),
        mdDiv(
            mdBold(mdText('Hello')), mdText('Everyone')
        )
    )
)

print(md.html)
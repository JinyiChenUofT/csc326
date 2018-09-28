<!DOCTYPE html>

<html>
<header>

    <title>Our Search Engine. </title>

    <link rel="stylesheet" type="text/css" href="homepage.css">

</header>

<body>

<h1>Search for "{{keywords}}"</h1>

% if len(words_count) > 1:
<table id=”results”>
    <tr>
        <td>Word</td>
        <td>Count</td>
    </tr>
%   for word in words_count:
    <tr>
        <td>{{word}}</td>
        <td>{{words_count[word]}}</td>
    </tr>
%   end
</table>
% end

<h2>Search history:</h2>


<table id=”history”>
    <tr>
        <td>Keywords</td>
        <td>Times Searched</td>
    </tr>
% for entry in history:
    <tr>
        <td>{{entry[0]}}</td>
        <td>{{entry[1][0]}}</td>
    </tr>
% end
</table>

</body>
</html>
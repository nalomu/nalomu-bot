<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
    <link href="https://fonts.googleapis.com/css?family=Noto+Serif+SC&display=swap&subset=chinese-simplified"
          rel="stylesheet">
    <style>
        * {
            font-family: 'Noto Serif SC', serif !important;
        }

        html, body {
            width: 500px
        }
            % if cover:
                body {
                    background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), url('https://nalomu.tk/bg.jpg') no-repeat center;
                    background-size: cover;
                }
            % endif
    </style>
</head>
<body>
    ${self.body()}
</body>
</html>
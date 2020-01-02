<%doc>
:see https://dev.heweather.com/docs/api/air:
</%doc>
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>天气</title>
    <link href="https://fonts.googleapis.com/css?family=Noto+Serif+SC&display=swap&subset=chinese-simplified"
          rel="stylesheet">
    <style>
        * {
            font-family: 'Noto Serif SC', serif !important;
        }

        body {
            overflow: hidden;
        }

        html, body {
            width: 1000px;
        }

            <%
                import random
                image = random.choice([
                    'weather-bg.jpg',
                    'weather-bg2.jpg',
                    'weather-bg3.jpg',
                    'weather-bg4.png',
                    'weather-cha.jpg',
                ])
                url = 'file:///{data_root}/images/{image}'.format(data_root=data_root,image=image)

            %>
        .container-fluid {
            background: linear-gradient(rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.3)),
            url('${url}') no-repeat top;
            background-size: cover;
        }

        #content {
            min-height: 400px;
            background-color: #0009;
            border-radius: 3px;
            border: 1px solid #fff;
            color: #eee;
            font-size: 20px;
        }
    </style>
</head>
<body>
<div class="container-fluid p-5">
    <%
        city = air_quality.basic.location
        now = air_quality.air_now_city

    %>
    <div class="row">
        <div class="offset-6 col" id="content">
            <div>城市：${city}</div>
            <div>数据发布时间：${now.pub_time}</div>
            <div>空气质量指数：${now.aqi}</div>
            <div>主要污染物：${now.main}</div>
            <div>空气质量：${now.qlty}</div>
            <div>pm10：${now.pm10}</div>
            <div>pm25：${now.pm25}</div>
            <div>二氧化氮：${now.no2}</div>
            <div>二氧化硫：${now.so2}</div>
            <div>一氧化碳：${now.co}</div>
            <div>臭氧：${now.o3}</div>
        </div>
    </div>
</div>
</body>
</html>

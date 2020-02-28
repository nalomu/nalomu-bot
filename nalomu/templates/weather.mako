<%doc>
:see https://dev.heweather.com/docs/api/weather:
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
                import urllib.parse
                url = 'file:///{data_root}/images/weather-bg.jpg'.format(
                    data_root=urllib.parse.quote(data_root.replace('\\','/'), safe='/:',))
            %>
        .container-fluid {
            ## background: -webkit-gradient(linear,top,bottom, color-stop(0%,#0003),color-stop(100%,url('${url}'))) no-repeat top; /* 支持 Chrome 25 and Safari 6, iOS 6.1, Android 4.3 */
            ## background: -moz-linear-gradient(#0003, #0003, url('${url}')) no-repeat top; /* 支持 Firefox (3.6 to 15) */
            ## background: -o-linear-gradient(#0003, #0003, url('${url}')) no-repeat top; /* 支持旧 Opera (11.1 to 12.0) */
            background: -webkit-gradient(linear, left top, left bottom, color-stop(0%, rgba(255, 255, 255, .3)), color-stop(100%, rgba(255, 255, 255, .3))), url('${url}');
            background: linear-gradient(rgba(255, 255, 255, .3), rgba(255, 255, 255, .3)), url('${url}') no-repeat top; /* 标准语法; 需要最新版本 */
            background-size: cover;
        }

        #content {
            min-height: 400px;
            background-color: rgba(0, 0, 0, .7);
            border-radius: 3px;
            border: 1px solid #fff;
            color: #eee;
            font-size: 20px;
        }
    </style>
</head>
<body>
<div class="container-fluid p-5">
    <div class="row">
        <div class="offset-6 col" id="content">
            % if isinstance(weather, list):
                <div>城市：${weather[0]['city']}</div>
            % for w in weather:
                <div>日期：${w['date']}</div>
                <div class="row">
                    <div class="col">白天天气： ${w['cond_txt_n']}</div>
                    <div class="col">晚上天气：${w['cond_txt_d']}</div>
                </div>
                <div class="row">
                    <div class="col">风力：${w['wind_sc']}</div>
                    <div class="col">风向：${w['wind_dir']}</div>
                </div>
                <div class="row">
                    <div class="col">最低气温：${w['tmp_min']}&#8451;</div>
                    <div class="col">最高气温：${w['tmp_max']}&#8451;</div>
                </div>
                <hr>
            % endfor
            %else:
                <div>城市：${weather['city']}</div>
                <div>天气：${weather['cond_txt']}</div>
                <div>风力：${weather['wind_sc']}</div>
                <div>风向：${weather['wind_dir']}</div>
                <div>风速：${weather['wind_spd']}km/h</div>
                <div>体感温度：${weather['fl']}&#8451;</div>
                <div>温度：${weather['tmp']}&#8451;</div>
                <div>相对湿度：${weather['hum']}%RH</div>
                <div>降水量：${weather['pcpn']}mm</div>
                <div>大气压强：${weather['pres']}hPa</div>
                <div>能见度：${weather['vis']}km</div>
                <div>云量：${weather['cloud']}</div>
            % endif
        </div>
    </div>
</div>
</body>
</html>

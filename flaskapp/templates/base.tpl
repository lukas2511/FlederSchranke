<html>
<head>
    <style type="text/css">
    html{
        background: #000000;
        color: #ffffff;
    }
    h1 {
        margin: 0;
    }
    .one {
        color: #FF0000;
    }
    .zero {
        color: #00FF00;
    }
    .flippy {
        color: #FFA000;
    }
    a {
        color: #ffffff;
        text-decoration: underline;
    }
    .seperator {
        color: #9999FF;
    }
    </style>
    <title>{{ title }}</title>
</head>
<body>
<h1>{% if h1 %}{{ h1 }}{% else %}{{ title }}{% endif %}</h1>
{%block content%}{%endblock%}
</body>
</html>
{% extends "base.tpl" %}
{% block content %}
<ul>
{% for key, bat_log in bat_logs_list %}
<li><a href="/bats/{{ bat_log.date.strftime('%Y/%m/%d') }}">{{ bat_log.date.strftime('%d.%m.%Y') }}</a></li>
{% endfor %}
</pre>
</ul>
{% endblock %}
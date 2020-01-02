<%inherit file="/layout.mako"/>
% if plugin:
    <div class="card">
        <div class="card-header">
            ${plugin.name}
        </div>
        <div class="card-body">
            <pre style="-ms-word-wrap: break-word;word-wrap: break-word;">${plugin.usage}</pre>
        </div>
    </div>
%else:
    <div class="card">
        <div class="card-header">
            发送 帮助 [命令] 获取详细帮助
        </div>
        <ul class="list-group list-group-flush">
            % for p in plugins:
                <li class="list-group-item">${p.name}</li>
            % endfor
        </ul>
    </div>
% endif

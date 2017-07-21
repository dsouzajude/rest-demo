<%inherit file="layout.mako"/>

<%block name="title">
  Welcome
</%block>

<%block name="content">
  <table>
    <tr>
      <td colspan="2">Logins</td>
    </tr>
    % for login in logins:
    <tr>
      <td colspan="2">${login['login_time']}</td>
    </tr>
    % endfor
  </table>
</%block>

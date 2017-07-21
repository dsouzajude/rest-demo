<%inherit file="layout.mako"/>

<%block name="title">
  Login
</%block>

<%block name="content">
  <form action="/login" method="post">
    <table>
      <tr>
        <td>username</td>
        <td><input name="username" id="username" type="text"></input></td>
      </tr>
      <tr>
        <td>password</td>
        <td><input name="password" id="username" type="password"></input></td>
      </tr>
      <tr>
        <td colspan="2">
          <button type="submit">Login</button>
        </td>
      </tr>
    </table>
  </form>
</%block>

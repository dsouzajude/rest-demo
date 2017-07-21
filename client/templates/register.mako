<%inherit file="layout.mako"/>

<%block name="title">
  Register
</%block>

<%block name="content">
  <form action="/register" method="post">
    <table>
      <tr>
        <td>Fullname</td>
        <td><input name="full_name" id="full_name" type="text"></input></td>
      </tr>
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
          <button type="submit">Register</button>
        </td>
      </tr>
    </table>
  </form>
</%block>

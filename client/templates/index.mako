<%inherit file="layout.mako"/>

<%block name="title">
  Register or Login
</%block>

<%block name="content">
  <form method="post">
    <table>
      <tr>
        <td>
          <a href="/register">
            <button type="button">Register</button>
          </a>
        </td>
        <td>
          <a href="/login">
            <button type="button">Login</button>
          </a>
        </td>
      </tr>
    </table>
  </form>
</%block>

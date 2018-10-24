<!DOCTYPE html>

<html>

<header>
    <link rel="icon" href="./assets/image/icon.ico">
    <title>Waldoge Search</title>
    <link rel="stylesheet" type="text/css" href="./assets/css/query_page.css">
    <link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
</header>


<body>
    
    <!-- the logo image -->
    <img class="title_image" src="./assets/image/waldoge.png">
    <!-- if user has not logged in, display the log_in button -->
    % if login == False:
    <form id="login_form" action="/login" method="get">
        <input id="login_button" class="btn btn-info btn-lg" value="Sign in" type="submit">
    </form>
    <!-- if user has logged in, display the user email, user name... -->
    %else:
    <form id="login_form">
        <button id="user_email" type="button" class="btn btn-info btn-lg" 
                data-toggle="modal" data-target="#logout_modal">{{user_email}}</button>
        <!--
        <button id="user_name" type="button" class="btn btn-info btn-lg">{{user_name}}</button>
        -->
    </form>
    %end

    <!-- form with a input box and a search button -->
    <form id="search_form" action="/" method="post" >
        <input id="input_box" name="keywords" type="text" placeholder=" Where's waldoge? ">            
        <input id="search_button" value="Waldoge Search" type="submit">

        %if login and history:
          %length=len(history)
          %print "length: "+repr(length)
        <table id="topSearchedTable">
         <tr>
         <th colspan="{{length}}" style="font-size:20px">Top Searched Words</th>
         </tr> 
         <tr>
          %for entry in history:
            %print entry[0]
            <th>{{entry[0]}}</th>
          %end
         </tr>
        </table>
        %end
    </form>


    %if login:
    <!-- log out modal --> 
    <form action="/logout" method="get">
    <div class="modal" id="logout_modal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">{{user_name}}</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <p>{{user_email}}</p>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <button type="submit" class="btn btn-primary">Sign out</button>
      </div>
    </div>
    </div>
    </div>
    </form>
    %end
</body>

</html>


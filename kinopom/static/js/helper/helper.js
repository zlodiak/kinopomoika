(function (){
    // -------------------------------------------------------------------------------------- share_button
    $("#shareButton").click(function(){
        $("#panel").slideToggle("slow");
        $(this).toggleClass("active"); 
        return false;
    });
    
    $('#myTab a').click(function (e) {
        e.preventDefault()
        $(this).tab('show')
    })
	// -------------------------------------------------------------------------------------- logout
	$('#logoutButton').on('click', function(event){	
        $.ajax({
            url: "/accounts/logout/",
            type: 'POST',
            dataType:"json",
            data: {
            	"csrfmiddlewaretoken": $('#registrationForm input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data) {
                if(data.result){
                	$('#regModal').modal('hide');

                	$('#guestPanel').addClass('show').removeClass('hide');
                	$('#userPanel').addClass('hide').removeClass('show');

	                $('#commonModalLabel').text('Вы вышли');
	                $('#modalDialog').addClass('modal-sm');
	                $('#butCancel').addClass('hide');
	                $('#commonModal').modal('show');

	                setTimeout(function(){
	                    $('#commonModal').modal('hide');
                        location.reload();
	                }, 1000); 
                }
            }
        }); 		
	});

	// -------------------------------------------------------------------------------------- auth button click
	$('#authButton').on('click', function(event){	
		$('#authModal').modal('show');			
	});

    //$().ready(function() {
        $("#authForm").validate({
	        submitHandler: function(){
 	            var flag = false,
	                username = $('#authForm .auth_username input'),
	                password = $('#authForm .auth_password input'),                       
	                usernameVal = $.trim(username.val()),
	                passwordVal = $.trim(password.val()),                     
	                csrfmiddlewaretokenVal = $('#authForm input[name=csrfmiddlewaretoken]').val();

	            $.ajax({
	                url: "/accounts/authentication/",
	                type: 'POST',
	                dataType:"json",
	                data: {
	                    "username": usernameVal,
	                    "password": passwordVal,
	                    "csrfmiddlewaretoken": csrfmiddlewaretokenVal
	                },
	                error: function(xhr, ajaxOptions, thrownError) {
	                    //console.log(xhr.status);
	                    //console.log(xhr.responseText);
	                    //console.log(thrownError);                 
	                },
	                success: function(data) {
	                    username.val('');
	                    password.val('');

	                	if(data.result){
		                    $('#authModal').modal('hide');

		                    $('#commonModalLabel').text('Вы авторизовались');
		                    $('#modalDialog').addClass('modal-sm');
		                    $('#butCancel').addClass('hide');
		                    $('#commonModal').modal('show');

		                   	//$('.username_mark_inner').text(usernameVal);
		                	//$('#guestPanel').addClass('hide').removeClass('show');
		                	//$('#userPanel').addClass('show').removeClass('hide');                      

		                    setTimeout(function(){
		                        $('#commonModal').modal('hide');
                                location.reload();
		                    }, 1000); 
	                    }
                        else{
		                    $('#authModal').modal('hide');

		                    $('#commonModalLabel').text('Не верные реквизиты для авторизации');
		                    $('#modalDialog').addClass('modal-sm');
		                    $('#butCancel').addClass('hide');
		                    $('#commonModal').modal('show');

		                    setTimeout(function(){
		                        $('#commonModal').modal('hide');
		                    }, 1000); 
	                    };  
	                }
	            });
	        },
            rules: {
                username: {
                    required: true,
                    maxlength: 30,
                    minlength: 3
                },
                password: {
                    required: true,
                    maxlength: 30,
                    minlength: 6
                }
            },
            messages: {
                username: {
                    required: "Введите имя",
                    minlength: "Введите не менее 3 символов",
                    maxlength: "Введите не более 30 символов"
                },
                password: {
                    required: "Введите пароль",
                    minlength: "Введите не менее 6 символов",
                    maxlength: "Введите не более 30 символов"
                }
            }
        });
    //});		

	// -------------------------------------------------------------------------------------- reg button click
	$('#regButton').on('click', function(event){	
		$('#regModal').modal('show');			
	});	

    $("#registrationForm").validate({
        submitHandler: function() {
            var flag = false,
                username = $('#id_username'),
                email = $('#id_email'),
                password1 = $('#id_password1'),
                password2 = $('#id_password2'),                        
                is_staff = $('#id_is_staff'),                        
                usernameVal = $.trim(username.val()),
                emailVal = $.trim(email.val()),
                password1Val = $.trim(password1.val()),
                password2Val = $.trim(password2.val()),                        
                is_staffVal = $.trim(is_staff.val()),                        
                csrfmiddlewaretokenVal = $('#registrationForm input[name=csrfmiddlewaretoken]').val();

            $.ajax({
                url: "/accounts/ajax_reg_form_check/",
                type: 'POST',
                dataType:"json",
                data: {
                    "username": usernameVal,
                    "email": emailVal,
                    "csrfmiddlewaretoken": csrfmiddlewaretokenVal
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    //console.log(xhr.status);
                    //console.log(xhr.responseText);
                    //console.log(thrownError);                 
                },
                success: function(data) {
                    //console.log(data.result);

                    if(data.username){
                        // ret true - matched, no reg
                        //username.addClass('shine');
                        $('#id_username').after('<label class="error">Имя занято</label>');
                        flag = true;
                    }
                    else{
                        // ret true - no matched, ok reg
                        //username.removeClass('shine');
                        $('#id_username .error').remove();
                    }


                    if(data.email){
                        // ret true - matched, no reg
                        $('#id_email').after('<label class="error">Имя занято</label>');
                        flag = true;
                    }
                    else{
                        // ret true - no matched, ok reg
                        $('#id_email .error').remove();
                    }                            
                },
                complete: function(){
                    if(!flag){
                        $.ajax({
                            url: "/accounts/registration/",
                            type: 'POST',
                            dataType:"json",
                            data: {
                                "username": usernameVal,
                                "email": emailVal,
                                "password1": password1Val,
                                "password2": password2Val,
                                "is_staff": is_staffVal,
                                "csrfmiddlewaretoken": $('#registrationForm input[name=csrfmiddlewaretoken]').val()
                            },
                            error: function(xhr, ajaxOptions, thrownError) {
                                //console.log(xhr.status);
                                //console.log(xhr.responseText);
                                //console.log(thrownError);                 
                            },
                            success: function(data) {
                                username.val('');
                                email.val('');
                                password1.val('');
                                password2.val('');

                                $('#regModal').modal('hide');

                                if(data.result){
                                    $('#commonModalLabel').text('Регистрация завершена');
                                }
                                else{
                                    $('#commonModalLabel').text('Ошибка регистрации');
                                };

                                $('#modalDialog').addClass('modal-sm');
                                $('#butCancel').addClass('hide');
                                $('#commonModal').modal('show');                                

                                setTimeout(function(){
                                    $('#commonModal').modal('hide');
                                }, 1000); 
                            }
                        }); 
                    }
                }
            });
        },        	
        rules: {
            username: {
                required: true,
                maxlength: 30,
                minlength: 3
            },
            password1: {
                required: true,
                maxlength: 30,
                minlength: 6
            },
            password2: {
                required: true,
                maxlength: 30,
                minlength: 6,
                equalTo: "#id_password1"
            },
            email: {
                required: true,
                maxlength: 30,
                minlength: 6,                            
                email: true
            }
        },
        messages: {
            username: {
                required: "Введите имя",
                minlength: "Введите не менее 3 символов",
                maxlength: "Введите не более 30 символов"
            },
            password1: {
                required: "Введите пароль",
                minlength: "Введите не менее 6 символов",
                maxlength: "Введите не более 30 символов"
            },
            password2: {
                required: "Введите пароль",
                minlength: "Введите не менее 6 символов",
                maxlength: "Введите не более 30 символов",
                equalTo: "Пароли должны совпадать"
            },
            email: {
                required: "Введите email",
                minlength: "Введите не менее 6 символов",
                maxlength: "Введите не более 30 символов",                 
                email: "Введите корректный email"                    
            }
        }
    });

/*	$('#registrationSubmit').on('click', function(e){
		var	flag = false,
			username = $('#id_username'),
			email = $('#id_email'),
			password1 = $('#id_password1'),
			password2 = $('#id_password2'),
			usernameVal = $.trim(username.val()),
			emailVal = $.trim(email.val()),
			password1Val = $.trim(password1.val());
			password2Val = $.trim(password2.val());

		e.preventDefault();

		if(!usernameVal || usernameVal.length < 3 || usernameVal.length > 30){
			username.addClass('shine');
			flag = true;
		}
		else{
			username.removeClass('shine');
		};

		if(!emailVal || emailVal.length < 6 || emailVal.length > 30){
			email.addClass('shine');
			flag = true;
		}
		else{
			email.removeClass('shine');
		};

		if(!password1Val || password1Val.length < 6 || password1Val.length > 30){
			password1.addClass('shine');
			flag = true;
		}
		else{
			password1.removeClass('shine');
		};	

		if(!password2Val || password2Val.length < 6 || password2Val.length > 30 || password1Val != password2Val){
			password2.addClass('shine');
			flag = true;
		}
		else{
			password2.removeClass('shine');
		};		

		$.ajax({
			url: "/accounts/ajax_username_check/",
			type: 'POST',
			dataType:"json",
			data: {
				"username": usernameVal,
				"csrfmiddlewaretoken": $('#registrationForm input[name=csrfmiddlewaretoken]').val()
			},
			error: function(xhr, ajaxOptions, thrownError) {
				//console.log(xhr.status);
				//console.log(xhr.responseText);
				//console.log(thrownError);					
			},
			success: function(data) {
				//console.log(data.result);

				if(data.result){
					// ret true - matched, no reg
					username.addClass('shine');
					flag = true;
				}
				else{
					// ret true - no matched, ok reg
					username.removeClass('shine');
				}
			},
			complete: function(){
				console.log(flag);

				if(!flag){
					console.log('create');
					$.ajax({
						url: "/accounts/registration/",
						type: 'POST',
						dataType:"json",
						data: {
							"username": usernameVal,
							"email": emailVal,
							"password1": password1Val,
							"password2": password2Val,
							"csrfmiddlewaretoken": $('#registrationForm input[name=csrfmiddlewaretoken]').val()
						},
						error: function(xhr, ajaxOptions, thrownError) {
							//console.log(xhr.status);
							//console.log(xhr.responseText);
							//console.log(thrownError);					
						},
						success: function(data) {
							//console.log('success');

							username.val('');
							email.val('');
							password1.val('');
							password2.val('');

							$('#regModal').modal('hide');

							$('#commonModalLabel').text('Регистрация завершена успешно');
							$('#modalDialog').addClass('modal-sm');
							$('#butCancel').addClass('hide');
							$('#commonModal').modal('show');

							setTimeout(function(){
								$('#commonModal').modal('hide');
							}, 1000);	
						}
					});		
				}
				else{
					//console.log('no create');
				};				
			}
		});	


	});		*/


})();


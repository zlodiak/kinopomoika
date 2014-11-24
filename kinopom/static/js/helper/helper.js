(function (){
    // -------------------------------------------------------------------------------------- related video on search page
    $('#search_results_articles .result_unit').on('mouseenter', function(){
        var num = $(this).attr('data-rel');

        $('#related_for_search .rel_group').css('display', 'none');
        $('#related_for_search .rel_group[data-rel="' + num + '"]').stop().fadeIn(1000);
    });

    // -------------------------------------------------------------------------------------- tags menu active punkt
    tagsActivePunkt();

    function tagsActivePunkt(){
        var tagMenuPunkts = $('#tagsContaiter li a'),
            pathname = location.pathname,
            pathnameList = pathname.split('/'),
            slug3 = pathnameList[3];        

        $.each(tagMenuPunkts, function(index, value){
            $(this).removeClass('active');

            if($(this).attr('data-href') == slug3){
                $(this).addClass('active');
            };
        });   
    }
     

    // -------------------------------------------------------------------------------------- tags menu more button
    var countAllTags = parseInt($('#countAllTags').text(), 10),
        countPageTags = $('#tagsContaiter li').length,
        csrfmiddlewaretokenVal = $('#tagsMoreForm input[name=csrfmiddlewaretoken]').val();

    $('.tags_list .more_button').hide();

    if(countAllTags > countPageTags){
        $('.tags_list .more_button').show(1000);
    };

    $('.tags_list .more_button').on('click', function(event){
        event.preventDefault();

        $.ajax({
            url: "/menu/tags/",
            type: 'POST',
            dataType:"json",
            data: {
                "countPageTags": countPageTags,
                "csrfmiddlewaretoken": csrfmiddlewaretokenVal
            },        
            success: function(data) {   
                data = JSON.parse(data);

                $.each(data, function(){
                    $('#tagsContaiter').append('<li><a data-href="' + this.pk + '" href="/menu/tags/' + this.pk + '">' + this.fields.title + '</li>');                 
                }); 
            },
            complete: function(){
                countPageTags = countPageTags + 12;
                if(countAllTags <= countPageTags){
                    $('.tags_list .more_button').hide();  
                };     

                console.log(3434);

                tagsActivePunkt();     
            }
        });         
    }); 
        
    
    // -------------------------------------------------------------------------------------- to start
    var pathname = location.pathname,
        pathnameList = pathname.split('/'),
        slug1 = pathnameList[1];

    if(slug1){
        $('#toStart').css('display', 'block');
    }
    else{
        $('#toStart').css('display', 'none');
    };

    $('.to_start').filter(':after').click(function(e) {
        e.preventDefault()
        console.log(44);
    })    

    // -------------------------------------------------------------------------------------- to top
    $(window).scroll(function() {
        if($(this).scrollTop() != 0) {
            $('#toTop').fadeIn();   
        } else {
            $('#toTop').fadeOut();
        }
    });
 
    $('#toTop').click(function() {
        $('body,html').animate({scrollTop:0},800);
    })

    // -------------------------------------------------------------------------------------- comment form ajax
    $('#commentForm').on('submit', function(e){
        e.preventDefault()
    });

    $('#id_comment').on('keypress', function(e){
        if(e.keyCode == 13){
            var video_id = parseInt($('#videoIdComment').attr('data-video-id'), 10),
                username = $.trim($('.username_comment').val()),
                comment = $.trim($('.comment_comment').val()),
                csrfmiddlewaretokenVal = $('#commentForm input[name=csrfmiddlewaretoken]').val();

            if(comment.length > 0){
                $.ajax({
                    url: "/comments/ajax_comment_add/",
                    type: 'POST',
                    dataType:"json",
                    data: {
                        "video_id": video_id,
                        "username": username,
                        "comment": comment,
                        "csrfmiddlewaretoken": csrfmiddlewaretokenVal
                    },
                    success: function(data) {
                        if(data.result){
                            // delete values from fields
                            $('.username_comment, .comment_comment').val('');

                            // add comment to end of list comments
                            $('#articlesComments').prepend('<article class="article comment_item"> \
                                                            <h5 class="h5"> \
                                                                <span class="name"> \
                                                                    ' + data.output_username + ' \
                                                                </span> \
                                                                <span class="date">' + data.date + '</span> \
                                                            </h5> \
                                                            <div class="body"> \
                                                                ' + comment + ' \
                                                            </div> \
                                                        </article>');
                        }                
                        else{
                            $('#commonModalLabel').text('Ошибка подключения');
                            $('#modalDialog').addClass('modal-xs');
                            $('#commonModal .modal-body').html('Попробуйте позже.');
                            $('#butCancel').addClass('hide');
                            $('#commonModal').modal('show');

                            setTimeout(function(){
                                $('#commonModal').modal('hide');
                            }, 1000); 
                        };
                    } 
                 });   
            }
            else{
                // delete values from fields
                $('.username_comment, .comment_comment').val('');

                // output error message
                $('#commonModalLabel').text('Введите комментарий');
                $('#modalDialog').addClass('modal-xs');
                $('#commonModal .modal-body').html('');
                $('#butCancel').addClass('hide');
                $('#commonModal').modal('show');

                setTimeout(function(){
                    $('#commonModal').modal('hide');
                }, 1000); 
            };
        }
    });

    // -------------------------------------------------------------------------------------- link_share
    $(".link_share").click(function(){
        $(".link_share").trigger("select");
    });

    $(".link_share_html").click(function(){
        $(".link_share_html").trigger("select");
    });    

    // -------------------------------------------------------------------------------------- likeButton
    $('#likeButton').on('click', function(event){   
        var video_id = parseInt($(this).attr('data-video-id'), 10),
            csrfmiddlewaretokenVal = $('#likeForm input[name=csrfmiddlewaretoken]').val();

        $.ajax({
            url: "/accounts/ajax_like/",
            type: 'POST',
            dataType:"json",
            data: {
                "video_id": video_id,
                "csrfmiddlewaretoken": csrfmiddlewaretokenVal
            },
            success: function(data) {
                var likesVal = parseInt($('#likesVal').text(), 10);

                if(data.is_authenticated){
                    if(data.is_authenticated){
                        $('#likesVal').html(likesVal + data.action)
                    };
                    console.log(data.action);
                }
                else{
                    $('#commonModalLabel').text('Вы не авторизованы');
                    $('#modalDialog').addClass('modal-md');
                    $('#commonModal .modal-body').html('Для того чтобы была возможность ставить лайки необходимо <a id="authLike" href="#">войти</a> в систему. \
                        Если у вас нет аккаунта, то необходимо <a id="regLike" href="#">зарегистрироваться.</a>');
                    $('#butOk').addClass('hide');
                    $('#commonModal').modal('show');

                    setTimeout(function(){
                        $('#commonModal').modal('hide');
                    }, 10000); 

                    $('#authLike').on('click', function(e){
                        e.preventDefault()
                        $('#commonModal').modal('hide');
                        $('#authButton').trigger('click');
                    });                    

                    $('#regLike').on('click', function(e){
                        e.preventDefault()
                        $('#commonModal').modal('hide');
                        $('#regButton').trigger('click');
                    });
                }                          
            }
        });  


    });

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
                            $('#commonModal .modal-body').empty();
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
                        $('#id_email').after('<label class="error">Email занят</label>');
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


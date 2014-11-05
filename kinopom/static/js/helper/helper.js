(function (){
	// -------------------------------------------------------------------------------------- auth button click
	$('#authButton').on('click', function(event){	
		$('#authModal').modal('show');			
	});

	// -------------------------------------------------------------------------------------- reg button click
	$('#regButton').on('click', function(event){	
		$('#regModal').modal('show');			
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
							}, 2000);	
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


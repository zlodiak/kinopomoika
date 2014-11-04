(function (){
	// -------------------------------------------------------------------------------------- auth button click
	$('#authButton').on('click', function(event){	
		$('#authModal').modal('show');			
	});

	// -------------------------------------------------------------------------------------- reg button click
	$('#regButton').on('click', function(event){	
		$('#regModal').modal('show');			
	});	

	var	form = $('#registrationForm');

	form.ajaxForm();

	$('#registrationSubmit').on('click', function(e){
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

		console.log(flag);

		if(!flag){
			form.ajaxSubmit({
			    url: form.action,
			    type : form.method,
			    data: $(form).serialize(),
				success: function (data) {
					console.log('success');

					username.val('');
					email.val('');
					password1.val('');
					password2.val('');

					$('#regModal').modal('hide');

					$('#commonModal').text('Сообщение отправлено');
					$('#commonModal').modal('show');

					setTimeout(function(){
						$('#commonModal').modal('hide');
					}, 2000);					
				}
			});
		};
	});
	


})();


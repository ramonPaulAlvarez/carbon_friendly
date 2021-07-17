function enableContactInputs(){
    $("#contact-form input").prop("disabled", false);
    $("#contact-form textarea").prop("disabled", false);
    $("#contact-form #submit").prop("disabled", false);
}

function submitContactForm(){
    // Disable Inputs
    $("#contact-form #submit").val("Sending...");
    $("#contact-form input").prop("disabled", true);
    $("#contact-form textarea").prop("disabled", true);
    $("#contact-form #submit").prop("disabled", true);

    let email = $("#contact-form #email").val();
    let subject = $("#contact-form #subject").val();
    let message = $("#contact-form #message").val();
    $.ajax({
        type: "POST",
        url: '/contact',
        data: {email: email, subject: subject, message: message},
    })
    .done((result) => {
        if (result.error){
            console.log(result.error);
            enableContactInputs();
            $("#contact-form #submit").val("Retry");
        } else {
            $("#contact-form #submit").val(result.success);
        }
    })
    .fail((jqXHR, textStatus, error) => {
        console.log(error);
        $("#contact-form #submit").val(error);
        enableContactInputs();
    });

}

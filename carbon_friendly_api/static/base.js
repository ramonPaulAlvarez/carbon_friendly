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

    // Submit payload
    $.ajax({
        type: "POST",
        url: '/contact',
        data: {from_email: email, subject: subject, message: message},
    })
    .done((result) => {
        $("#contact-form #submit").val(result.success);
    })
    .fail((jqXHR, textStatus, error) => {
        console.log(JSON.parse(jqXHR.responseText));
        $("#contact-form #submit").val(error);
        enableContactInputs();
    });

}

from django.core.validators import RegexValidator


phone_regex = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="Phone number must be 7–15 digits and may start with +"
)



#ID Validations
id_number_validator = RegexValidator(
    regex=r'^\d{2}-\d{6,7}[A-Za-z]\d{2}$',
    message=(
        "ID number must be in the format: "
        "NN-NNNNNN(L)NN or NN-NNNNNNN(L)NN "
        "(e.g. 43-123678K76)"
    )
)
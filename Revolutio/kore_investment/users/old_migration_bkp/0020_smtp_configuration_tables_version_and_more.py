# Generated by Django 4.0.10 on 2023-05-04 06:36

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "users",
            "0019_rename_category_subelement_attributes_category_subelement_category_subelement_attributes_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="smtp_configuration",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("app_code", models.CharField(max_length=255, null=True)),
                ("element_id", models.TextField(blank=True, null=True)),
                ("server_name", models.CharField(max_length=255, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("group_assigned", models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name="tables",
            name="version",
            field=models.CharField(default="1.0.0", max_length=10, verbose_name="Version"),
        ),
        migrations.AddField(
            model_name="tabscreens",
            name="update_version",
            field=models.CharField(default="1.0.0", max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="countrymaster",
            name="active_from",
            field=models.DateField(blank=True, null=True, verbose_name="Active From"),
        ),
        migrations.AlterField(
            model_name="countrymaster",
            name="active_to",
            field=models.DateField(null=True, verbose_name="Active To"),
        ),
        migrations.AlterField(
            model_name="countrymaster",
            name="country_name",
            field=models.CharField(
                choices=[
                    ("Aruba", "Aruba"),
                    ("Afghanistan", "Afghanistan"),
                    ("Angola", "Angola"),
                    ("Anguilla", "Anguilla"),
                    ("Åland Islands", "Åland Islands"),
                    ("Albania", "Albania"),
                    ("Andorra", "Andorra"),
                    ("United Arab Emirates", "United Arab Emirates"),
                    ("Argentina", "Argentina"),
                    ("Armenia", "Armenia"),
                    ("American Samoa", "American Samoa"),
                    ("Antarctica", "Antarctica"),
                    ("French Southern Territories", "French Southern Territories"),
                    ("Antigua and Barbuda", "Antigua and Barbuda"),
                    ("Australia", "Australia"),
                    ("Austria", "Austria"),
                    ("Azerbaijan", "Azerbaijan"),
                    ("Burundi", "Burundi"),
                    ("Belgium", "Belgium"),
                    ("Benin", "Benin"),
                    ("Bonaire, Sint Eustatius and Saba", "Bonaire, Sint Eustatius and Saba"),
                    ("Burkina Faso", "Burkina Faso"),
                    ("Bangladesh", "Bangladesh"),
                    ("Bulgaria", "Bulgaria"),
                    ("Bahrain", "Bahrain"),
                    ("Bahamas", "Bahamas"),
                    ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
                    ("Saint Barthélemy", "Saint Barthélemy"),
                    ("Belarus", "Belarus"),
                    ("Belize", "Belize"),
                    ("Bermuda", "Bermuda"),
                    ("Bolivia, Plurinational State of", "Bolivia, Plurinational State of"),
                    ("Brazil", "Brazil"),
                    ("Barbados", "Barbados"),
                    ("Brunei Darussalam", "Brunei Darussalam"),
                    ("Bhutan", "Bhutan"),
                    ("Bouvet Island", "Bouvet Island"),
                    ("Botswana", "Botswana"),
                    ("Central African Republic", "Central African Republic"),
                    ("Canada", "Canada"),
                    ("Cocos (Keeling) Islands", "Cocos (Keeling) Islands"),
                    ("Switzerland", "Switzerland"),
                    ("Chile", "Chile"),
                    ("China", "China"),
                    ("Côte d'Ivoire", "Côte d'Ivoire"),
                    ("Cameroon", "Cameroon"),
                    ("Congo, The Democratic Republic of the", "Congo, The Democratic Republic of the"),
                    ("Congo", "Congo"),
                    ("Cook Islands", "Cook Islands"),
                    ("Colombia", "Colombia"),
                    ("Comoros", "Comoros"),
                    ("Cabo Verde", "Cabo Verde"),
                    ("Costa Rica", "Costa Rica"),
                    ("Cuba", "Cuba"),
                    ("Curaçao", "Curaçao"),
                    ("Christmas Island", "Christmas Island"),
                    ("Cayman Islands", "Cayman Islands"),
                    ("Cyprus", "Cyprus"),
                    ("Czechia", "Czechia"),
                    ("Germany", "Germany"),
                    ("Djibouti", "Djibouti"),
                    ("Dominica", "Dominica"),
                    ("Denmark", "Denmark"),
                    ("Dominican Republic", "Dominican Republic"),
                    ("Algeria", "Algeria"),
                    ("Ecuador", "Ecuador"),
                    ("Egypt", "Egypt"),
                    ("Eritrea", "Eritrea"),
                    ("Western Sahara", "Western Sahara"),
                    ("Spain", "Spain"),
                    ("Estonia", "Estonia"),
                    ("Ethiopia", "Ethiopia"),
                    ("Finland", "Finland"),
                    ("Fiji", "Fiji"),
                    ("Falkland Islands (Malvinas)", "Falkland Islands (Malvinas)"),
                    ("France", "France"),
                    ("Faroe Islands", "Faroe Islands"),
                    ("Micronesia, Federated States of", "Micronesia, Federated States of"),
                    ("Gabon", "Gabon"),
                    ("United Kingdom", "United Kingdom"),
                    ("Georgia", "Georgia"),
                    ("Guernsey", "Guernsey"),
                    ("Ghana", "Ghana"),
                    ("Gibraltar", "Gibraltar"),
                    ("Guinea", "Guinea"),
                    ("Guadeloupe", "Guadeloupe"),
                    ("Gambia", "Gambia"),
                    ("Guinea-Bissau", "Guinea-Bissau"),
                    ("Equatorial Guinea", "Equatorial Guinea"),
                    ("Greece", "Greece"),
                    ("Grenada", "Grenada"),
                    ("Greenland", "Greenland"),
                    ("Guatemala", "Guatemala"),
                    ("French Guiana", "French Guiana"),
                    ("Guam", "Guam"),
                    ("Guyana", "Guyana"),
                    ("Hong Kong", "Hong Kong"),
                    ("Heard Island and McDonald Islands", "Heard Island and McDonald Islands"),
                    ("Honduras", "Honduras"),
                    ("Croatia", "Croatia"),
                    ("Haiti", "Haiti"),
                    ("Hungary", "Hungary"),
                    ("Indonesia", "Indonesia"),
                    ("Isle of Man", "Isle of Man"),
                    ("India", "India"),
                    ("British Indian Ocean Territory", "British Indian Ocean Territory"),
                    ("Ireland", "Ireland"),
                    ("Iran, Islamic Republic of", "Iran, Islamic Republic of"),
                    ("Iraq", "Iraq"),
                    ("Iceland", "Iceland"),
                    ("Israel", "Israel"),
                    ("Italy", "Italy"),
                    ("Jamaica", "Jamaica"),
                    ("Jersey", "Jersey"),
                    ("Jordan", "Jordan"),
                    ("Japan", "Japan"),
                    ("Kazakhstan", "Kazakhstan"),
                    ("Kenya", "Kenya"),
                    ("Kyrgyzstan", "Kyrgyzstan"),
                    ("Cambodia", "Cambodia"),
                    ("Kiribati", "Kiribati"),
                    ("Saint Kitts and Nevis", "Saint Kitts and Nevis"),
                    ("Korea, Republic of", "Korea, Republic of"),
                    ("Kuwait", "Kuwait"),
                    ("Lao People's Democratic Republic", "Lao People's Democratic Republic"),
                    ("Lebanon", "Lebanon"),
                    ("Liberia", "Liberia"),
                    ("Libya", "Libya"),
                    ("Saint Lucia", "Saint Lucia"),
                    ("Liechtenstein", "Liechtenstein"),
                    ("Sri Lanka", "Sri Lanka"),
                    ("Lesotho", "Lesotho"),
                    ("Lithuania", "Lithuania"),
                    ("Luxembourg", "Luxembourg"),
                    ("Latvia", "Latvia"),
                    ("Macao", "Macao"),
                    ("Saint Martin (French part)", "Saint Martin (French part)"),
                    ("Morocco", "Morocco"),
                    ("Monaco", "Monaco"),
                    ("Moldova, Republic of", "Moldova, Republic of"),
                    ("Madagascar", "Madagascar"),
                    ("Maldives", "Maldives"),
                    ("Mexico", "Mexico"),
                    ("Marshall Islands", "Marshall Islands"),
                    ("North Macedonia", "North Macedonia"),
                    ("Mali", "Mali"),
                    ("Malta", "Malta"),
                    ("Myanmar", "Myanmar"),
                    ("Montenegro", "Montenegro"),
                    ("Mongolia", "Mongolia"),
                    ("Northern Mariana Islands", "Northern Mariana Islands"),
                    ("Mozambique", "Mozambique"),
                    ("Mauritania", "Mauritania"),
                    ("Montserrat", "Montserrat"),
                    ("Martinique", "Martinique"),
                    ("Mauritius", "Mauritius"),
                    ("Malawi", "Malawi"),
                    ("Malaysia", "Malaysia"),
                    ("Mayotte", "Mayotte"),
                    ("Namibia", "Namibia"),
                    ("New Caledonia", "New Caledonia"),
                    ("Niger", "Niger"),
                    ("Norfolk Island", "Norfolk Island"),
                    ("Nigeria", "Nigeria"),
                    ("Nicaragua", "Nicaragua"),
                    ("Niue", "Niue"),
                    ("Netherlands", "Netherlands"),
                    ("Norway", "Norway"),
                    ("Nepal", "Nepal"),
                    ("Nauru", "Nauru"),
                    ("New Zealand", "New Zealand"),
                    ("Oman", "Oman"),
                    ("Pakistan", "Pakistan"),
                    ("Panama", "Panama"),
                    ("Pitcairn", "Pitcairn"),
                    ("Peru", "Peru"),
                    ("Philippines", "Philippines"),
                    ("Palau", "Palau"),
                    ("Papua New Guinea", "Papua New Guinea"),
                    ("Poland", "Poland"),
                    ("Puerto Rico", "Puerto Rico"),
                    ("Korea, Democratic People's Republic of", "Korea, Democratic People's Republic of"),
                    ("Portugal", "Portugal"),
                    ("Paraguay", "Paraguay"),
                    ("Palestine, State of", "Palestine, State of"),
                    ("French Polynesia", "French Polynesia"),
                    ("Qatar", "Qatar"),
                    ("Réunion", "Réunion"),
                    ("Romania", "Romania"),
                    ("Russian Federation", "Russian Federation"),
                    ("Rwanda", "Rwanda"),
                    ("Saudi Arabia", "Saudi Arabia"),
                    ("Sudan", "Sudan"),
                    ("Senegal", "Senegal"),
                    ("Singapore", "Singapore"),
                    (
                        "South Georgia and the South Sandwich Islands",
                        "South Georgia and the South Sandwich Islands",
                    ),
                    (
                        "Saint Helena, Ascension and Tristan da Cunha",
                        "Saint Helena, Ascension and Tristan da Cunha",
                    ),
                    ("Svalbard and Jan Mayen", "Svalbard and Jan Mayen"),
                    ("Solomon Islands", "Solomon Islands"),
                    ("Sierra Leone", "Sierra Leone"),
                    ("El Salvador", "El Salvador"),
                    ("San Marino", "San Marino"),
                    ("Somalia", "Somalia"),
                    ("Saint Pierre and Miquelon", "Saint Pierre and Miquelon"),
                    ("Serbia", "Serbia"),
                    ("South Sudan", "South Sudan"),
                    ("Sao Tome and Principe", "Sao Tome and Principe"),
                    ("Suriname", "Suriname"),
                    ("Slovakia", "Slovakia"),
                    ("Slovenia", "Slovenia"),
                    ("Sweden", "Sweden"),
                    ("Eswatini", "Eswatini"),
                    ("Sint Maarten (Dutch part)", "Sint Maarten (Dutch part)"),
                    ("Seychelles", "Seychelles"),
                    ("Syrian Arab Republic", "Syrian Arab Republic"),
                    ("Turks and Caicos Islands", "Turks and Caicos Islands"),
                    ("Chad", "Chad"),
                    ("Togo", "Togo"),
                    ("Thailand", "Thailand"),
                    ("Tajikistan", "Tajikistan"),
                    ("Tokelau", "Tokelau"),
                    ("Turkmenistan", "Turkmenistan"),
                    ("Timor-Leste", "Timor-Leste"),
                    ("Tonga", "Tonga"),
                    ("Trinidad and Tobago", "Trinidad and Tobago"),
                    ("Tunisia", "Tunisia"),
                    ("Turkey", "Turkey"),
                    ("Tuvalu", "Tuvalu"),
                    ("Taiwan, Province of China", "Taiwan, Province of China"),
                    ("Tanzania, United Republic of", "Tanzania, United Republic of"),
                    ("Uganda", "Uganda"),
                    ("Ukraine", "Ukraine"),
                    ("United States Minor Outlying Islands", "United States Minor Outlying Islands"),
                    ("Uruguay", "Uruguay"),
                    ("United States", "United States"),
                    ("Uzbekistan", "Uzbekistan"),
                    ("Holy See (Vatican City State)", "Holy See (Vatican City State)"),
                    ("Saint Vincent and the Grenadines", "Saint Vincent and the Grenadines"),
                    ("Venezuela, Bolivarian Republic of", "Venezuela, Bolivarian Republic of"),
                    ("Virgin Islands, British", "Virgin Islands, British"),
                    ("Virgin Islands, U.S.", "Virgin Islands, U.S."),
                    ("Viet Nam", "Viet Nam"),
                    ("Vanuatu", "Vanuatu"),
                    ("Wallis and Futuna", "Wallis and Futuna"),
                    ("Samoa", "Samoa"),
                    ("Yemen", "Yemen"),
                    ("South Africa", "South Africa"),
                    ("Zambia", "Zambia"),
                    ("Zimbabwe", "Zimbabwe"),
                ],
                default="India",
                max_length=100,
                unique=True,
                verbose_name="Country",
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="date_joined",
            field=models.DateTimeField(blank=True, null=True, verbose_name="date joined"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="username",
            field=models.CharField(
                db_index=True,
                help_text="Required. 150 characters or fewer. Letters, numbers and @/./+/-/_ characters",
                max_length=150,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[\\w.@+-]+$", 152), "Enter a valid username.", "invalid"
                    )
                ],
                verbose_name="username",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="date_joined",
            field=models.DateTimeField(blank=True, null=True, verbose_name="date joined"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="first_name",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="last_name",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="username",
            field=models.CharField(
                db_index=True,
                help_text="Required. 150 characters or fewer. Letters, numbers and @/./+/-/_ characters",
                max_length=150,
                null=True,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[\\w.@+-]+$", 152), "Enter a valid username.", "invalid"
                    )
                ],
                verbose_name="username",
            ),
        ),
    ]

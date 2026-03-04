## Payment SATIM

- Add reCaptcha keys in website module (Developer mode > Website > Configurations menu > Websites > `reCAPTCHA keys` tab)
- Payment mode must be `active` (Invoicing > Configuration > Payement method)
- Update `translation` if updates are not visible (Parameters > Translations)
- Set `Default/Portal/Public users template` timezone to Africa/Algeirs
- Update sale order sequence by extending it to 10 caracters (Parameters > technical > sequences > search for sale.order > set `Prefix` to `S%(y)s` and sequence length to `7` ) 
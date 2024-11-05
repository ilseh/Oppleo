/* 
  

*/

    // From simplewebauthn-browser (function a())
    function toArrayBuffer(e) {
      for (var t = e.replace(/-/g, "+").replace(/_/g, "/"), r = (4 - t.length % 4) % 4, n = t.padEnd(t.length + r, "="), o = atob(n), i = new ArrayBuffer(o.length), a = new Uint8Array(i), s = 0; s < o.length; s++)
          a[s] = o.charCodeAt(s)
      return i
    }

    function fromArrayBuffer(e) {
        var t, r, n = new Uint8Array(e), o = "";
        try {
            for (var i = function(e) {
                var t = "function" == typeof Symbol && Symbol.iterator
                  , r = t && e[t]
                  , n = 0;
                if (r)
                    return r.call(e);
                if (e && "number" == typeof e.length)
                    return {
                        next: function() {
                            return e && n >= e.length && (e = void 0),
                            {
                                value: e && e[n++],
                                done: !e
                            }
                        }
                    };
                throw new TypeError(t ? "Object is not iterable." : "Symbol.iterator is not defined.")
            }(n), a = i.next(); !a.done; a = i.next()) {
                var s = a.value;
                o += String.fromCharCode(s)
            }
        } catch (e) {
            t = {
                error: e
            }
        } finally {
            try {
                a && !a.done && (r = i.return) && r.call(i)
            } finally {
                if (t)
                    throw t.error
            }
        }
        return btoa(o).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "")
    }

    function base64URLdecode(str) {
      const base64Encoded = str.replace(/-/g, '+').replace(/_/g, '/')
      const padding = str.length % 4 === 0 ? '' : '='.repeat(4 - (str.length % 4))
      const base64WithPadding = base64Encoded + padding
      return atob(base64WithPadding)
        .split('')
        .map(char => String.fromCharCode(char.charCodeAt(0)))
        .join('')
    }

    async function registerNewPasskey(csrf_token) {

      // https://docs.yubico.com/hardware/yubikey-guidance/best-practices/sp-bestpractices-passkeys.html
      // navigator.credentials &&
      // navigator.credentials.create &&
      // navigator.credentials.get &&
      // window.PublicKeyCredential

      if (typeof navigator.credentials != 'object' || 
          typeof navigator.credentials.create != 'function' ||
          webauthnRegistrationOptions == undefined ) {
        autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
        return
      }

      let rCredential = undefined

      let excludeCredentials = webauthnRegistrationOptions.excludeCredentials.map((credential) => ({ ...credential, id: toArrayBuffer( credential.id ) }) )
      //let excludeCredentials1 = webauthnRegistrationOptions.excludeCredentials.map((credential) => ({ ...credential, id: toArrayBuffer( base64URLdecode( credential.id ) ) }) )
      excludeCredentials.forEach( (excludeCredentials, i) => {
        excludeCredentials.transports = [ 'nfc', 'usb' ]
      })

      const abortController = new AbortController()
      try {
        // --- AUTORISE PASSKEY LOCAL
        const publicKeyCredentialCreationOptions = {
            challenge: new TextEncoder().encode( webauthnRegistrationOptions.challenge ),
            rp: {
                name: webauthnRegistrationOptions.rp.name,
                id: webauthnRegistrationOptions.rp.id,
            },
            user: {
                id: new TextEncoder().encode( webauthnRegistrationOptions.user.id ),
                name: webauthnRegistrationOptions.user.name,
                displayName: webauthnRegistrationOptions.user.displayName,
            },
            pubKeyCredParams: webauthnRegistrationOptions.pubKeyCredParams,
            excludeCredentials: excludeCredentials,
            authenticatorSelection: webauthnRegistrationOptions.authenticatorSelection,
            timeout: webauthnRegistrationOptions.timeout,
            attestation: webauthnRegistrationOptions.attestation
        }
        if ('residentKey' in publicKeyCredentialCreationOptions.authenticatorSelection &&
            publicKeyCredentialCreationOptions.authenticatorSelection.residentKey.toLowerCase() != 'discouraged') {
          publicKeyCredentialCreationOptions.extensions = publicKeyCredentialCreationOptions.extensions || {} // Create if it doesn't exist
          publicKeyCredentialCreationOptions.extensions.credProps = true
        }
        rCredential = await navigator.credentials.create({
            publicKey: publicKeyCredentialCreationOptions,
            signal: abortController.signal
        })

      } catch (error) {
        console.error('WebAuthN ' + error.name + ': ' + error.message)
        if (['InvalidStateError', 'AbortError', 'NotAllowedError'].includes(error.name)) {
          // "The authenticator was previously registered"
          autoHideNotify('warning','top-left', 'WebAuthN', error.message)
        } else {
          autoHideNotify('warning','top-left', 'WebAuthN', 'WebAuthN unbekende fout. WebAuthN niet beschikbaar.')
        }

        $('.spinner').hide()
        return
      }

      rawId = fromArrayBuffer( rCredential.rawId )

      // --- REGISTER PASSKEY ON SERVER
      $('.spinner').show()
      data = {
            csrf_token : csrf_token,
            webauthnId : rCredential.id,
            webauthnResponse: JSON.stringify( rCredential.toJSON() ),
          }      
      $.ajax({
        type		    : 'POST',
        url			    : ('/webauthn/registration/'),
        dataType	  : 'json',
        headers     : { 'ignore-login-next': 'true' },
        encode		  : true,
        data        : data
      }) // using the done promise callback
      .done(function(data) {
        // log data to the console so we can see
        let _csrf_token = csrf_token
        console.log(data)
        switch (data.status) {
          case 200:
            // Add key to the list
            if (!$('tr#passkey-'+data.credential.id).length) {
              $('table#passkey-list tr:last').after('<tr id="passkey-'+data.credential.id+'"><td></td><td><oppleo-edit-str id="passkey-'+data.credential.id+'" prefix="" value="'+data.credential.name+'" validation="^([0-9]|[a-z]|[A-Z]|[!@#$%^&*()-+._/\\\[\]{}\',:;|&quot; ]|[ ])+$" info="Herkenbare naam voor credential met id '+data.credential.id+'." delete="true" /></td></tr>')
              // Oppleo web component applied change
              $('oppleo-edit-str#passkey-'+data.credential.id).on('apply', (e) => {
                console.log('oppleo-edit-str onApply [' + e.target.id + '] oldValue:' + e.detail.oldValue + ' newValue:' + e.detail.newValue)
                // Submit
                let credentialId = e.target.id.substring(8, e.target.id.length)
                updateProfile( _csrf_token, credentialId, 'rename', e.detail.newValue )
              })
              // Oppleo web component delete
              $('oppleo-edit-str#passkey-'+data.credential.id).on('delete', (e) => {
                console.log('oppleo-edit-str onDelete [' + e.target.id + '] oldValue:' + e.detail.oldValue + ' newValue:' + e.detail.newValue)

                showConfirmModal(
                    '<i class="fas fa-exclamation-triangle"></i> Verwijder', 
                    'Verwijder credential <span class="text-dark"><strong>' + e.target.$input.value + '</strong></span>?', 
                    () => { 
                      // Delete
                      let credentialId = e.target.id.substring(8, e.target.id.length)
                      updateProfile( _csrf_token, credentialId, 'delete', e.detail.newValue )
                    }
                  )
              })
            }
            if ($('oppleo-edit-str[id^=passkey-]').length > 0) {
              $('button#validate-passkey').removeClass('d-none')
              $('button#discoverable-credential-passkey').removeClass('d-none')
            }
            autoHideNotify('success','top-left', 'WebAuthN', 'Passkey geregistreerd.')
            break
          default:
            autoHideNotify('warning','top-left', 'WebAuthN', 'WebAuthN niet beschikbaar.')
            break
        }
      })
      .fail(function(data) {
        autoHideNotify('warning','top-left', 'WebAuthN', 'WebAuthN niet beschikbaar.')
        console.error("WebAuthN error: "+data.responseJSON.msg)
      })
      .always(function() {
        // Remove spinner
        $('.spinner').hide()
      })
    }

    async function getWebauthnCredentials(csrf_token) {

      data = {
            csrf_token : csrf_token
          }
      $.ajax({
        type		    : 'GET',
        url			    : ('/webauthn/credentials/'),
        headers     : { 'ignore-login-next': 'true' },
        dataType	  : 'json',
        headers     : { 'ignore-login-next': 'true' },
        encode		  : true,
        data        : data,
        cache       : false
      }) // using the done promise callback
      .done(function(data) {
        let _csrf_token = csrf_token
        // log data to the console so we can see
        console.log(data)
        switch (data.status) {
          case 200:
            webauthnRegisteredCredentials = JSON.parse(data.credentials)
            // Add keys to the list
            webauthnRegisteredCredentials.forEach( (e, i) => {
              if (!$('tr#passkey-'+e.id).length) {
                $('table#passkey-list tr:last').after('<tr id="passkey-'+e.credential_id+'"><td></td><td><oppleo-edit-str id="passkey-'+e.credential_id+'" prefix="" value="'+(e.name!=""?e.name:'Key '+(i+1))+'" validation="^([0-9]|[a-z]|[A-Z]|[!@#$%^&*()-+._/\\\[\]{}\',:;|&quot; ]|[ ])+$" info="Herkenbare naam voor credential met id '+e.credential_id+'." delete="true" /></td></tr>')
                // Oppleo web component applied change
                $('oppleo-edit-str#passkey-'+e.credential_id).on('apply', (e) => {
                  console.log('oppleo-edit-str onApply [' + e.target.id + '] oldValue:' + e.detail.oldValue + ' newValue:' + e.detail.newValue)
                  // Submit
                  let credentialId = e.target.id.substring(8, e.target.id.length)
                  updateProfile( _csrf_token, credentialId, 'rename', e.detail.newValue )
                })
                // Oppleo web component delete
                $('oppleo-edit-str#passkey-'+e.credential_id).on('delete', (e) => {
                  showConfirmModal(
                    '<i class="fas fa-exclamation-triangle"></i> Verwijder', 
                    'Verwijder credential <span class="text-dark"><strong>' + e.target.$input.value + '</strong></span>?', 
                    () => { 
                      // Delete
                      let credentialId = e.target.id.substring(8, e.target.id.length)
                      updateProfile( _csrf_token, credentialId, 'delete', e.detail.newValue )
                    }
                  )
                })
              }
            })
            if ($('oppleo-edit-str[id^=passkey-]').length > 0) {
              $('button#validate-passkey').removeClass('d-none')
              $('button#discoverable-credential-passkey').removeClass('d-none')
            }
            break
          default:
            autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
            // Remove spinner
            $('.spinner').hide()
            break
        }
      })
      .fail(function(data) {
        autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
        // Remove spinner
        $('.spinner').hide()
      })
      .always(function() {
      })
    }
      

    async function getWebauthnAuthenticationOptions(csrf_token, login=false, username=undefined) {
      // --- FETCH PASSKEY AUTHENTICATION OPTIONS

      // Show spinner
      $('.spinner').show()

      data = {
            csrf_token : csrf_token
          }
      if (username != undefined) {
        data.username = username
      }
      $.ajax({
        type		    : 'GET',
        url			    : ('/webauthn/authentication/'),
        headers     : { 'ignore-login-next': 'true' },
        dataType	  : 'json',
        headers     : { 'ignore-login-next': 'true' },
        encode		  : true,
        data        : data,
        cache       : false
      }) // using the done promise callback
      .done(function(data) {
        const _credentialUser = data.username
        let _login = login
        // log data to the console so we can see
        console.log(data)
        switch (data.status) {
          case 200:
            let _csrf_token = csrf_token
            webauthnAuthenticationOptions = JSON.parse(data.options)
            validatePasskey(_csrf_token, _login, _credentialUser)
            break
          case 424: // Failed dependencies
            autoHideNotify('warning','top-left', 'WebAuthN', 'Geen WebAuthN registraties voor authorisatie.')
            break
          default:
            autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
            // Remove spinner
            $('.spinner').hide()
            break
        }
      })
      .fail(function(data) {
        autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
        // Remove spinner
        $('.spinner').hide()
      })
      .always(function() {
      })
    }

    async function validatePasskey(csrf_token, login=false, credentialUser=undefined) {
      // --- VERIFY PASSKEY (AUTHENTICATE)

      if (typeof navigator.credentials != 'object' || 
          typeof navigator.credentials.get != 'function' ||
          webauthnAuthenticationOptions == undefined ) {
        autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
        return
      }

      // Credential IDs to ArrayBuffer
      let allowCredentials = webauthnAuthenticationOptions.allowCredentials.map((credential) => ({ ...credential, id: toArrayBuffer( credential.id ), transports: ['usb', 'ble', 'nfc'] }) )

      let aAssertion = undefined
      try {
        const publicKeyCredentialRequestOptions = {
          challenge: new TextEncoder().encode( webauthnAuthenticationOptions.challenge ),
          allowCredentials: allowCredentials,
          rpId: webauthnAuthenticationOptions.rpId,
          timeout: webauthnAuthenticationOptions.timeout,
        }

        aAssertion = await navigator.credentials.get({
          publicKey: publicKeyCredentialRequestOptions
        })


      } catch (error) {
        console.error(error)
        autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
        $('.spinner').hide()
        return
      }

      // --- VALIDATE PASSKEY ON SERVER
      data = {
            csrf_token : csrf_token,
            webauthnId : aAssertion.id,
            webauthnResponse: JSON.stringify( aAssertion.toJSON() )
          }
      if (credentialUser != undefined) {
        data.username = credentialUser
      }
      $.ajax({
        type		    : 'POST',
        url			    : ('/webauthn/authentication/'),
        dataType	  : 'json',
        headers     : { 'ignore-login-next': 'true' },
        encode		  : true,
        data        : data
      }) // using the done promise callback
      .done(function(data) {
        let _login = login
        // log data to the console so we can see        
        console.log(data)
        switch (data.status) {
          case 200:
            autoHideNotify('success','top-left', 'WebAuthN', 'User ' + data.User?.displayName + ' succesvol gevalideerd door ' + data.keyname + '.')
            // Login or validation?
            if (_login) {
              if (data.login_next) {
                window.location.replace( 
                  location.protocol + '//' + location.host + data.login_next
                )
              } else {
                // window.history.go(-1) shows a page like you are not logged in
                window.location.replace( 
                  (document.referrer.length > 0 && document.referrer.split('/')[2] == location.host) ? 
                    // Referrer, go back if it is on the same host
                    document.referrer :
                    // No referrer or not on this host, go to the default page
                    location.protocol + '//' + location.host + '/'
                )
              }
            }
            break
          default:
            autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
            break
        }
      })
      .fail(function(data) {
        autoHideNotify('warning','top-left', 'Onbekend', 'WebAuthN niet beschikbaar.')
      })
      .always(function() {
        // Remove spinner
        $('.spinner').hide()
      })


      let i = 0

    }    


function updateProfile( csrf_token, credentialId, action, value ) {
  console.log(timestamp() + ' updateProfile()')            
  // Show spinner
  $('.spinner').show()
  if (value === true) value = 'true'
  if (value === false) value = 'false'     
  data = {
        csrf_token    : csrf_token,
        credentialId  : credentialId,
        action        : action,
        value         : value
      }
  $.ajax({
    type		    : 'POST',
    url			    : '/webauthn/credentials/',
    dataType	  : 'json',
    headers     : { 'ignore-login-next': 'true' },
    encode		  : true,
    data        : data,
    cache       : false
  }) // using the done promise callback
  .done(function(data) {
    // log data to the console so we can see
    console.log(data)
    switch (data.status) {
      case 200:
        switch (data.action) {
          case 'rename':
            autoHideNotify('success', 'top-left', 'Passkey', 'Naam credential gewijzigd in '+data.value+'.')
            break
          case 'delete':
            $('tr#passkey-'+data.credentialId).each( (i, trId) => {
              trId.remove()
            })
            if ($('oppleo-edit-str[id^=passkey-]').length == 0) {
              $('button#validate-passkey').addClass('d-none')
              $('button#discoverable-credential-passkey').addClass('d-none')
            }
            autoHideNotify('success', 'top-left', 'Passkey', 'Naam credential '+data.name+' verwijderd.')
            break
          default:
            console.error("Unknkown action " + data.action + " completed for credential " + data.credentialId)
            autoHideNotify('warning','top-left', 'Foutmelding', 'Onbekende actie.')
            break
        }
        break
      case 400:
      case 404:
        autoHideNotify('warning', 'top-left', 'Foutmelding', 'Wijziging kon niet doorgevoerd worden. ' + data.reason)
        break
      default:
        autoHideNotify('warning','top-left', 'Foutmelding', 'Fout onbekend. Niet gewijzigd.')
        break
    }

  })
  .fail(function(data) {
    autoHideNotify('error','top-left', 'Connectie fout', 'Profiel niet gewijzigd.')
  })
  .always(function() {
    // Remove spinner
    $('.spinner').hide()
  })
}

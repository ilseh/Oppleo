/* 
  Oppleo Edit Select Web Component

  Import the following in the main file

  <!-- https://select2.org/ -->
  <link href="/static/plugins/select2/4.0.7/select2.min.css" rel="stylesheet" type="text/css" />
  <script src="/static/plugins/select2/4.0.7/select2.min.js" type="text/javascript"></script>

  Options: 
    - info is optional. 
    - unlock=true leaves selectbox open and does not trigger onApply event

  Dynamic update options example. Create a data Object 
    let dObj = []
    optionList.forEach( (v) => {
      dObj.push( { id: v, text: v  } )
    })
  Set options as jQuery property (object or string) or as HTMLElement attribute (string):
    $('oppleo-edit-select#id').prop('options', dObj)
    $('oppleo-edit-select#id').prop('options', JSON.stringify(dObj))
    $('oppleo-edit-select#id').attr('options', JSON.stringify(dObj))


*/

class OppleoEditSelect extends HTMLElement {

  constructor() {
    super()  

    // querySelector does not allow ID's staring with a digit!!!
    this.elId = "id_" + Math.random().toString(36).substr(2, 8)
    this.oppleo_edit_select_template = document.createElement('template');

    this.oppleo_edit_select_template.innerHTML = `
      <!-- App css -->
      <link rel="stylesheet" type="text/css" href="/static/plugins/bootstrap/4.4.1/css/bootstrap.min.css">
      <link rel="stylesheet" type="text/css" href="/static/css/icons.css">
      <link rel="stylesheet" type="text/css" href="/static/css/style.css">

      <script src="/static/js/jquery-3.3.1.js"></script>
      
      <script src="/static/plugins/bootstrap/4.4.1/js/bootstrap.min.js"></script>
      <script src="/static/js/waves.js"></script>

      <link href="/static/plugins/select2/4.0.7/select2.min.css" rel="stylesheet" />
      <script src="/static/plugins/select2/4.0.7/select2.min.js"></script>

      <link rel="stylesheet" type="text/css" href="/static/plugins/fontawesome/5.13.3/css/all.min.css">
      <link rel="stylesheet" type="text/css" href="/static/css/oppleo-edit-select.css">
      <style>

      </style>

      <div class="input-group">
        <span class="input-group-prepend">
          <span 
            class="input-group-text bg-dark b-1 text-secondary"
            id="info_text"
            style="display: none;"
            data-toggle="tooltip" 
            data-placement="bottom" 
            data-html="true" 
            title=""
            >
            <i class="fas fa-info-circle"></i>
          </span>
        </span>

        <span id="`+this.elId+`_select_container" class="input-group-addon" style="display: none; width: calc(100% - 130px);">
          <select 
            id="`+this.elId+`_select2_select"
            class="form-control select2 pb-5"
            style="width: 100%;"
            >
          </select>
        </span>

        <div class="form-control form-control-sm input-group-append bg-dark"
          id="`+this.elId+`_select_text"
          >
          <span class="input-group-text"
            id="text_value"
            >
          </span>
        </div>

        <span class="input-group-append">
          <button
            type="button" 
            id="`+this.elId+`_cancelButton"
            class="btn btn-sm pl-3 pr-3 waves-effect waves-light btn-secondary"
            style="display: none;"
            data-toggle="tooltip" 
            data-placement="bottom" 
            data-html="true" 
            title="<em>Annuleren</em>"
            >
            <i class="fas fa-times"></i>
          </button> 
          <button
            type="button" 
            id="`+this.elId+`_editApplyButton"
            class="btn btn-sm pl-3 pr-3 waves-effect waves-light btn-low-key-warning"
            data-toggle="tooltip" 
            data-placement="bottom" 
            data-html="true" 
            title="<em>Wijzigen</em>"
            >
            <i class="fas fa-lock"></i>
          </button> 
        </span>
      </div>`

    this.locked = true
    this.prevOptions = [] // Contains the state before opening, to return to on cancel
  
    this._shadowRoot = this.attachShadow({ mode: 'open' })
    this._shadowRoot.appendChild(this.oppleo_edit_select_template.content.cloneNode(true))

    this.$select = this._shadowRoot.querySelector('select#'+this.elId+'_select2_select')
    //this.$select = this._shadowRoot.querySelector('select')

    this.$select_container = this._shadowRoot.querySelector('#'+this.elId+'_select_container')    
    this.$text = this._shadowRoot.querySelector('div#'+this.elId+'_select_text')
    this.$info = this._shadowRoot.querySelector('span#info_text')
    this.$cancelButton = this._shadowRoot.querySelector('button#'+this.elId+'_cancelButton')
    this.$editApplyButton = this._shadowRoot.querySelector('button#'+this.elId+'_editApplyButton')
    this.$regex = undefined

    this.$info.addEventListener('mouseenter', () => { 
      $(this.$info).toggleClass("bg-dark", false)
      $(this.$info).toggleClass("bg-success", true)
      $(this.$info).toggleClass("text-muted", false)
      $(this.$info).toggleClass("text-light", true)
    })
    this.$info.addEventListener('mouseleave', () => { 
      $(this.$info).toggleClass("bg-dark", true)
      $(this.$info).toggleClass("bg-success", false)
      $(this.$info).toggleClass("text-muted", true)
      $(this.$info).toggleClass("text-light", false)
    })

    $(this.$select).on('select2:select', (e) => {
      this.dispatchEvent(
        new CustomEvent('select', {
            bubbles: true, 
            detail: { 
              id  : e.params.data.id,
              text: e.params.data.text
            }
        })
      )
    })
    $(this.$select).on('select2:unselect', (e) => {
      this.dispatchEvent(
        new CustomEvent('unselect', {
            bubbles: true, 
            detail: { }
        })
      )
    })

    this.$cancelButton.addEventListener('click', () => {

      // Cancelling, select the previous selected option
      this.locked = true
      this.options = this.prevOptions

      this.render() // or fire change?

    })
    this.$editApplyButton.addEventListener('click', () => {
      if (this.locked) {
        // Locked --> Unlock
        this.locked = false

        this.render() // or fire change?
      } else {
        this.locked = true

        // Apply (no validation, drop down selections only)
        let oldSEl = this.prevOptions.filter( (el) => { return (el.selected == true || el.selected === 'true') } )
        let evDetail = { 
          newText : $(this.$select).select2('data').map( (el) => { return el.text } ).join(', '),
          newValue: $(this.$select).select2('data').map( (el) => { return el.id } ).join(', '),
          oldText : oldSEl.map( (el) => {return el.text}).join(", "),
          oldValue: oldSEl.map( (el) => {return el.id}).join(", ")
        }

         // Save new state
        var lois = $(this.$select).select2('data').map( (el) => { return el.id } )
        let loc = this.options  // Local copy from attribute
        loc.forEach( (el) => { (lois.includes(el.id) ? el.selected = true : delete el.selected) }, loc)  // in place
        this.options = loc  // Set the attribute and the prevOptions

        // Value actually changed?
        if (evDetail.newValue !== evDetail.oldValue) {
            // Set the span text
          $(this.$text).find('span#text_value').text(evDetail.newText)
          this.dispatchEvent(
            new CustomEvent('apply', {
                bubbles: true, 
                detail: evDetail
            })
          )
        }
        this.render() // or fire change?
      }
    })

  }
  get id() {
    return this.getAttribute('id')
  }
  set id(value) {
    this.setAttribute('id', value)
  }
  get placeholder() {
    return this.getAttribute('placeholder')
  }
  set placeholder(value) {
    this.setAttribute('placeholder', value)
  }
  // The options property is an array of options 
  // Attributes can only contain a string, convert to array when reading
  get options() {
    return JSON.parse(this.getAttribute('options'))
  }
  // The options property should be an array of options.
  // Attributes can only contain a string, convert array to string when setting
  // Don't convert when the value is already a string
  set options(value) {
    if (typeof value !== "string") {
      this.setAttribute('options', JSON.stringify(value))
      this.prevOptions = value
    } else {
      this.setAttribute('options', value)
      this.prevOptions = JSON.parse(value)
    }
    if (this.prevOptions.filter( (el) => { return (el.selected == true || el.selected === 'true')} ).length == 0)
      $(this.$select).select2().val('').change()
  }
  get info() {
    return this.getAttribute('info')
  }
  set info(value) {
    this.setAttribute('info', value)
  }
  get unlock() {
    return (this.getAttribute('unlock') === 'true')
  }
  set unlock(value) {
    this.setAttribute('lock', value)
  }
  static get observedAttributes() {
    return ['info', 'options']
  }
  // Invoked each time one of the custom element's attributes is added, removed, or changed. 
  // Which attributes to notice change for is specified in a static get observedAttributes method
  attributeChangedCallback(name, oldVal, newVal) {
    switch (name) {
      case 'info':
        // Set the info tooltip text
        this.$info.setAttribute('data-original-title', this.info)
        break
      case 'options':
        $(this.$select).select2().empty()
        $(this.$select).select2({
          data: this.options
        }).trigger('change') //.change()
        // TODO for now unselect all - future select the options
        //$(this.$select).select2().val('').change()
        break
    }
    this.render()
  }
  // Called once after the oppleo-edit-select is attached to the DOM
  connectedCallback() {
    $(this.$info).tooltip({ boundary: 'window' })
    $(this.$cancelButton).tooltip({ boundary: 'window' })
    $(this.$editApplyButton).tooltip({ boundary: 'window' })

    $(this.$select).attr("data-placeholder", this.placeholder)
    // Fill the select2

    this.prevOptions = this.options

/*
    $(this.$select).select2({
      placeholder: this.placeholder,
      data: this.options// JSON.parse(this.options)
    }).trigger('change') // .change()
*/
    //.next().hide()
//    $(this.$select).hide()
    // Set the span text
    $(this.$text).find('span#text_value').text($(this.$select).find("option:selected").text())

    if (this.unlock) {
      //this.$editApplyButton.click()
    }

    this.render() // needed, doesn't call it by itself
  }
  close() {
    if ($(this.$select).hasClass("select2-hidden-accessible")) {
      // Select2 has been initialized
      $(this.$select).select2('close')
    }
  }
  // {data: [{id: 1, text: 'new text'}, {id: 2, text: 'new text'}]}
  // TO BE PHASED OUT - gebruik attribute en verander string. Moet gedetecteerd worden!
  updateOptionsX(options=this.options) {
    if (options != null && typeof options != 'object') { this.options = JSON.stringify(options.data)}
    if (options != null && typeof options != 'string') { this.options = options.data }

    $(this.$select).select2().empty()
    $(this.$select).select2({
      data: JSON.parse(this.options)
    })
    $(this.$select).select2().val('').change()
  }
  drawValidationBorder() {
  }
  render() {

    if (this.locked && !this.unlock) {
      // Locked
      $(this.$select).select2().next().hide()
      $(this.$select).hide()
      $(this.$select_container).hide()
      $(this.$text).show()
      if (this.info != null) $(this.$info).hide()
      $(this.$cancelButton).hide()
      this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
      this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
      this.$editApplyButton.classList.add("btn-low-key-warning")
      this.$editApplyButton.classList.remove("btn-primary")    


    } else {
        // Not locked or unlock
        $(this.$select).select2().next().show()
        $(this.$select).show()
        $(this.$select_container).show()
        $(this.$text).hide()
        if (this.info != null) $(this.$info).show()
        // Correct length for absent info box
        if (this.info == null) {
          $(this.$select_container).css('width', 'calc(100% - 88px)')
        }
        // If not locked, unlock and hide apply and cancel buttons
        if (this.unlock) {
          $(this.$cancelButton).hide()
          $(this.$editApplyButton).hide()
          if (this.info == null) {
            $(this.$select_container).css('width', 'calc(100% - 0px)')
          } else {
            $(this.$select_container).css('width', 'calc(100% - 42px)')
          }
        } else {
          $(this.$cancelButton).show()
          $(this.$editApplyButton).show()
        }
        $(this.$select).select2()
        //this.$cancelButton.style.display = ""
        this.$editApplyButton.setAttribute('data-original-title', '<em>Opslaan</em>')
        this.$editApplyButton.innerHTML = '<i class="far fa-save"></i>'
        this.$editApplyButton.classList.remove("btn-low-key-warning")
        this.$editApplyButton.classList.add("btn-primary")
    }
    this.$cancelButton.blur()
    this.$editApplyButton.blur()
    this.drawValidationBorder()  

  }

}
window.customElements.define('oppleo-edit-select', OppleoEditSelect)

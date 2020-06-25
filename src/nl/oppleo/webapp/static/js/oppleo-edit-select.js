/* 
  Oppleo Edit Select Web Component

  Import the following in the main file

  <!-- Select2 -->
  <link href="/static/plugins/select2/4.0.7/select2.min.css" rel="stylesheet" type="text/css" />
  <script src="/static/plugins/select2/4.0.7/select2.min.js" type="text/javascript"></script>


*/

const oppleo_edit_select_template = document.createElement('template');

oppleo_edit_select_template.innerHTML = `
  <!-- App css -->
  <link rel="stylesheet" type="text/css" href="/static/plugins/bootstrap/4.4.1/css/bootstrap.min.css">
  <link rel="stylesheet" type="text/css" href="/static/css/icons.css">
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">

  <script src="/static/js/jquery-3.3.1.js"></script>
  
  <script src="/static/plugins/bootstrap/4.4.1/js/bootstrap.min.js"></script>
  <script src="/static/js/waves.js"></script>

  <link href="/static/plugins/select2/4.0.7/select2.min.css" rel="stylesheet" />
  <script src="/static/plugins/select2/4.0.7/select2.min.js"></script>

  <link rel="stylesheet" type="text/css" href="/static/plugins/fontawesome/5.12.0/css/all.css">
  <link rel="stylesheet" type="text/css" href="/static/css/oppleo-edit-select.css">
  <style>

  </style>

  <div class="input-group">
    <span class="input-group-prepend">
      <span 
        class="input-group-text  bg-dark b-1 text-secondary"
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

    <select 
      class="form-control select2 pb-5"
      style="display: none;"
      >
      <option value="AK">Alaska</option>
      <option value="HI">Hawaii</option>
      <optgroup label="Pacific Time Zone">
          <option value="CA">California</option>
          <option value="NV">Nevada</option>
      </optgroup>
      <optgroup label="Mountain Time Zone">
        <option value="AK">Alaska</option>
        <option value="HI">Hawaii</option>
        <option value="AL">Alabama</option>
        <option value="AR">Arkansas</option>
        <option value="VA">Virginia</option>
        <option value="WV">West Virginia</option>
      </optgroup>
    </select>




    <div class="form-control form-control-sm input-group-append bg-dark"
      id="select_text"
      >
      <span class="input-group-text"
        id="text_value"
        >
      </span>
    </div>


    <span class="input-group-append">
      <button
        type="button" 
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

class OppleoEditSelect extends HTMLElement {
  constructor() {
    super()  

    this._shadowRoot = this.attachShadow({ mode: 'open' })
    this._shadowRoot.appendChild(oppleo_edit_select_template.content.cloneNode(true))

    this.$select = this._shadowRoot.querySelector('select')
    this.$text = this._shadowRoot.querySelector('div #select_text')
    this.$info = this._shadowRoot.querySelector('span#info_text')
    this.$cancelButton = this._shadowRoot.querySelector('button:nth-child(1)')
    this.$editApplyButton = this._shadowRoot.querySelector('button:nth-child(2)')
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

    this.$cancelButton.addEventListener('click', () => {
      // Cancel - Reset the selected option
      $(this.$select).find('option:contains(' + this.selectedText + ')').prop('selected', true)
      $(this.$select).select2().next().hide()
      $(this.$select).hide()
      $(this.$text).show()
      if (this.info != null) $(this.$info).hide()
      $(this.$cancelButton).hide()
      this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
      this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
      this.$editApplyButton.classList.add("btn-low-key-warning")
      this.$editApplyButton.classList.remove("btn-primary")    
      this.drawValidationBorder()  
    })
    this.$editApplyButton.addEventListener('click', () => {
      if (this.$editApplyButton.innerHTML.indexOf("fa-lock") >= 0) {
        // Unlock
        $(this.$select).select2().next().show()
        $(this.$select).show()

        $(this.$text).hide()
        if (this.info != null) $(this.$info).show()
        $(this.$cancelButton).show()
        $(this.$select).select2()
        this.$cancelButton.style.display = ""
        this.$editApplyButton.setAttribute('data-original-title', '<em>Opslaan</em>')
        this.$editApplyButton.innerHTML = '<i class="far fa-save"></i>'
        this.$editApplyButton.classList.remove("btn-low-key-warning")
        this.$editApplyButton.classList.add("btn-primary")
        this.$editApplyButton.blur()
      } else {
        // Apply (no validation, drop down selections only)
        let newValue = $(this.$select).find("option:selected").val()
        let newText = $(this.$select).find("option:selected").text()
        let oldText = this.selectedText
        let oldValue = $(this.$select).find('option:contains(' + this.selectedText + ')').val()

        $(this.$select).select2().next().hide()
        $(this.$select).hide()
        $(this.$text).show()
        if (this.info != null) $(this.$info).hide()
        $(this.$cancelButton).hide()
        this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
        this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
        this.$editApplyButton.classList.add("btn-low-key-warning")
        this.$editApplyButton.classList.remove("btn-primary")

        // Value actually changed?
        if (newValue !== oldValue) {
          this.selectedText = newText
            // Set the span text
          $(this.$text).find('span#text_value').text(newText)
          this.dispatchEvent(
            new CustomEvent('apply', {
                bubbles: true, 
                detail: { 
                  newText : newText,
                  newValue: newValue,
                  oldText : oldText,
                  oldValue: oldValue
                }
            })
          )
        }
        this.$editApplyButton.blur()
      }
    })

  }
  get id() {
    return this.getAttribute('id')
  }
  set id(value) {
    this.setAttribute('id', value)
  }
  get options() {
    return this.getAttribute('options')
  }
  set options(value) {
    this.setAttribute('options', value)
  }
  get selectedText() {
    return this.getAttribute('selectedText')
  }
  set selectedText(value) {
    this.setAttribute('selectedText', value)
  }
  get selectedValue() {
    return this.getAttribute('selectedValue')
  }
  set selectedValue(value) {
    this.setAttribute('selectedValue', value)
  }
  get info() {
    return this.getAttribute('info')
  }
  set info(value) {
    this.setAttribute('info', value)
  }
  static get observedAttributes() {
    return ['selectedText', 'selectedValue', 'info']
  }
  attributeChangedCallback(name, oldVal, newVal) {
    this.render()
  }
  connectedCallback() {
    $(this.$info).tooltip({ boundary: 'window' })
    $(this.$cancelButton).tooltip({ boundary: 'window' })
    $(this.$editApplyButton).tooltip({ boundary: 'window' })
    $(this.$select).select2().next().hide()
    $(this.$select).hide()
  }
  drawValidationBorder() {
  }
  render() {
    // Clear options list
    $(this.$select).find('option').remove()
    // Clear optgroups
    $(this.$select).find('optgroup').remove()
    // Add configured options to list
    let optArr = JSON.parse(this.options)
    for(let i = 0; i < optArr.length; i++) {
      if (optArr[i].optgroup != undefined) {
        // Add to optgroup, does it exist?
        let optgroup = undefined
        if ($(this.$select).find('optgroup[label="' + optArr[i].optgroup + '"]').length > 0) {
          // Exists, append
          optgroup = $(this.$select).find('optgroup[label="' + optArr[i].optgroup + '"]')
        } else {
          // Does not exist, create
          optgroup = $("<optgroup>")
          optgroup.attr('label', optArr[i].optgroup).appendTo(this.$select)  
        }
        $("<option>").val(optArr[i].value).text(optArr[i].text).appendTo(optgroup)
      } else {
        // Add directly
        $("<option>").val(optArr[i].value).text(optArr[i].text).appendTo(this.$select)
      }
    }
    // Select the selected option
    if (this.selectedText) {
      $(this.$select).find('option:contains(' + this.selectedText + ')').prop('selected', true)
    }
    if (this.selectedValue) {
      $(this.$select).find('option[value="' + this.selectedValue + '"]').prop('selected', true)
      // Set the selectedText from the selected option
      this.selectedText = $(this.$select).find('option[value="' + this.selectedValue + '"]').text()
    }
    // Set the span text
    $(this.$text).find('span#text_value').text(this.selectedText)
    // Set the info tooltip text
    this.$info.setAttribute('data-original-title', this.info)
  }
}
window.customElements.define('oppleo-edit-select', OppleoEditSelect)







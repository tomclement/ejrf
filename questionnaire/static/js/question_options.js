<<<<<<< Updated upstream
jQuery(function($){


=======
jQuery(function ($) {
>>>>>>> Stashed changes
    var $form = $("#id-new-question-form"),
        template = $("#question-option-template").html(),
        answerTypeSelect = $('#id_answer_type');

    function addQuestionOption($element){
        $element.before(template);
        assignOptionNumbers($form);
    }

    if(answerTypeSelect.val() == 'MultiChoice'){
        $('#option-choices').addClass('show').removeClass('hide');
    } else if (answerTypeSelect.val() == 'Date') {
        $("#id_answer_sub_type_span").show();
    }

    answerTypeSelect.on('change', function(){
        $('#option-choices').removeClass('show').addClass('hide');
        removeOptions();

        $("#id_answer_sub_type_span").hide();

        if($(this).val() == 'MultiChoice'){
            $('#option-choices').addClass('show').removeClass('hide');
<<<<<<< Updated upstream
        } else if ($(this).val() == 'Date') {
            $("#id_answer_sub_type_span").show();
=======
        } else if ($(this).val() == 'Date' || $(this).val() == 'Number') {
            showResponseSubType($(this).val());
        } else if ($(this).val() == 'CheckBox') {
            addQuestionOption($("div.form-actions"));
            $('input[name=options-custom]')[0].checked = true
>>>>>>> Stashed changes
        }
    });

    $('input[type=radio]').on('change', function(){
        if($(this).val() == 'custom'){
            addQuestionOption($("div.form-actions"));
            $form.find('input[name=options]').prop('checked', false);
        }else{
            $form.find('input[name=options-custom]').prop('checked', false);
            removeOptions()
        }
    });

    $form.on("click", ".add-option", function(){
        addQuestionOption($("div.form-actions"));
    });

    $form.on("click", ".remove-option", function(){
        $(this).parents("div#option-input-group").remove();
        assignOptionNumbers($form)
    });
});

function assignOptionNumbers($form){
    assignOptionNumbersUsing($form, "span.number");
    assignOptionNumbersUsing($form, "span.mid-table-number");
    assignIdsWithNumbers($form, 'select[name=columns]');
}   

function assignOptionNumbersUsing($form, number_selector){
        $form.find(number_selector).each(function(i, element){
            $(element).text(++i);
        });
    }

function assignIdsWithNumbers($form, inputName){
        $form.find(inputName).each(function(i, element){
            $(element).attr('id', 'id-column-' + i);
        });
    }

function removeOptions(){
        $("div.input-group").each(function(){
           $(this).remove();
        });
    }


$(document).ready( function() {
   $('.btn-file :file').on('fileselect', function(event, numFiles, label) {

       var input = $(this).parents('.input-group').find(':text'),
           log = numFiles > 1 ? numFiles + ' files selected' : label;

       if( input.length ) {
           input.val(log);
       } else {
           if( log ) alert(log);
       }

   });
});
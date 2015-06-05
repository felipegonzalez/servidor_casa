   $(document).ready(function() {
         
         $.get("/info_bas", {})
         .done(function(string){

          $("#estado").append(string);

         });
         $("#autoluces").click(function(e) {
           $.post("/autoluz", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
         

         $("#accion-garage").click(function(e) {
           $.post("/garage", {})
            .done(function(string) {
               $("#respuesta input").val(string);

            });
           e.preventDefault();
         });
         $("#accion-zumbador").click(function(e) {
           $.post("/zumbador", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
          $("#accion-alarma").click(function(e) {
           $.post("/alarma/1", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
     $("#accion-alarma2").click(function(e) {
           $.post("/alarma/0", {})
            .done(function(string) {
               $("#respuesta input").val(string);

            });
           e.preventDefault();
         });
      $("#aire").click(function(e) {
           $.post("/control_aire", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
        $("#dormir-a").click(function(e) {
           $.post("/dormir", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
        $("#lock-a").click(function(e) {   
         $.post("/chapa/1", {})
            .done(function(string) {
               $("#respuesta input").val(string);
               //$("#mi-mensaje").append(string);
            }); 
         });


        $("#unlock-a").click(function(e) {
           $.post("/chapa/0", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
        $("#luces-cocina").click(function(e) {
           $.post("/lucescocina", {})
            .done(function(string) {
               $("#respuesta input").val(string);

            });
           e.preventDefault();
         });
        $("#apagar-cocina").click(function(e) {
           $.post("/apagarcocina", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
      $("#apagar-luces").click(function(e) {
           $.post("/apagar_luces", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
  
       });
   $(document).ready(function() {
         
         $.get("/info_bas", {})
         .done(function(string){

            $("#estado").append(string);

         });
         $("#autoluces").click(function(e) {
           $.post("/autoluz", {}).done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
         
         $("#autoaire").click(function(e) {
           $.post("/auto_ac", {}).done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);
         });
          
          $("#accion-garage").click(function(e) {
           $.post("/garage", {}).done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);

         });
         $("#accion-zumbador").click(function(e) {
           $.post("/zumbador", {})
            .done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
         });
          $("#accion-alarma").click(function(e) {
           $.post("/alarma/1", {}).done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);

         });
     $("#accion-alarma2").click(function(e) {
           $.post("/alarma/0", {}).done(function(string) {
               $("#respuesta input").val(string);

            });
           e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);

         });
      $("#aire").click(function(e) {
           $.post("/control_aire", {}).done(function(string) {
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
         $.post("/chapa/1", {}).done(function(string) {
               $("#respuesta input").val(string);
            }); 
            e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);
         });
        $("#unlock-a").click(function(e) {
           $.post("/chapa/0", {}).done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);
         });
        $("#regar-on").click(function(e) {
           $.post("/regar/1", {}).done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);
         });
        $("#regar-off").click(function(e) {   
         $.post("/regar/0", {}).done(function(string) {
               $("#respuesta input").val(string);
            }); 
            e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);
         });


     
        $("#luces-cocina").click(function(e) {
           $.post("/lucescocina", {})
            .done(function(string) {
               $("#respuesta input").val(string);

            });
           e.preventDefault();
         });

        $("#llegar-caminando").click(function(e){
          $.post("/zumbador", {})
            .done(function(string) {
            });
          $.post("/chapa/0", {})
            .done(function(string) {
               $("#respuesta input").val(string);

            });
           e.preventDefault();
        });

        $("#llegar-coche").click(function(e){
          $.post("/garage", {})
            .done(function(string) {
            });
          $.post("/chapa/0", {})
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
           $.post("/apagar_luces", {}).done(function(string) {
               $("#respuesta input").val(string);
            });
           e.preventDefault();
           setTimeout(function(){location.reload()}, 2000);

         });
  
       });
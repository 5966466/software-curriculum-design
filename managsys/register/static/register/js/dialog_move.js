var Dragging=function(validateHandler){ 
    var draggingObj=null; //dragging Dialog
    var diffX=0;
    var diffY=0;
    
    function mouseHandler(e){
        switch(e.type){
            case 'mousedown':
                draggingObj=validateHandler(e);
                if(draggingObj!=null){
                    diffX=e.clientX-draggingObj.offsetLeft;
                    diffY=e.clientY-draggingObj.offsetTop;
                }
                break;
            
            case 'mousemove':
                if(draggingObj){
                    draggingObj.style.left=(e.clientX-diffX)+'px';
                    draggingObj.style.top=(e.clientY-diffY)+'px';
                }
                break;
            
            case 'mouseup':
                draggingObj =null;
                diffX=0;
                diffY=0;
                break;
        }
    };
    
    return {
        enable:function(){
            document.addEventListener('mousedown',mouseHandler);
            document.addEventListener('mousemove',mouseHandler);
            document.addEventListener('mouseup',mouseHandler);
        },
        disable:function(){
            document.removeEventListener('mousedown',mouseHandler);
            document.removeEventListener('mousemove',mouseHandler);
            document.removeEventListener('mouseup',mouseHandler);
        }
    }
}

function getDraggingDialog(e){
    var target=e.target;
    while(target && target.className.indexOf('dialog_form_title')==-1){
        target=target.offsetParent;
    }
    if(target!=null){
        return target.offsetParent;
    }else{
        return null;
    }
}

Dragging(getDraggingDialog).enable();
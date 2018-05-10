function setupNode(key_chain,value) {
   var newChild;
   for (var i = key_chain.length - 1; i >= 0; i--) {
        if (i == key_chain.length - 1) {
             newChild = {};
             newChild['name'] = key_chain[i];
             values = [];
             values.push({"name": value});
             newChild['children'] = values;
        }
        else {
             var newChildCopy = newChild;
             newChild = {};

             newChild['name'] = key_chain[i];
             newChild['children'] = [newChildCopy];
        }
   }

   return newChild
}


function addToNode(key_chain,node,node_path,value) {
   newChild = setupNode(key_chain,value);

   var exec_str = "node";

   for (var i = 0; i < node_path.length; i++) {
        exec_str += "[" + node_path[i] + "]['children']";
   }

   try {
        eval(exec_str + ".push(newChild)");
   }
   catch(err) {
        new_exec_str = exec_str;
        new_exec_str += "=[];"
        eval(new_exec_str);
        exec_str += ".push(newChild)";
        eval(exec_str);
   }

   return node
}

function createNodePath(i,key_chain,result) {
   node_path = [i];
   node = result[i]['children'];
   key_chain = key_chain.slice(1);

   var check = 0;

   for (var j = 0; j < key_chain.length; j++) {
        check = 0;
        for (var k = 0; k < node.length; k++) {
             if (key_chain[j] == node[k]['name']) {
                  node_path.push(k);
                  if (!!node[k]['children']) {
                       node = node[k]['children'];
                       check = 1;
                       break;
                  }
                  else {
                       node[k]['children'] = [];
                       check = 1;
                       break;
                  }
             }
        }
        if (!check) {
            break;
        }
   }

   return node_path
}

function parseTree(data) {
   var result = [];
   var keys = Object.keys(data);

   for (var i = 0; i < keys.length; i++) {
        key_chain = keys[i].replace("|","/").split("/");
        var value = data[keys[i]];

        for (var j = 0; j < result.length; j++) {
             if (result[j]['name'] == key_chain[0]){
                  node_path = createNodePath(j,key_chain,result);
                  result = addToNode(key_chain.slice(node_path.length),result,node_path,value);
                  break;
             }
             else {
                  if (j == result.length - 1) {
                       result.push(setupNode(key_chain,value));
                       break;
                  }
             }
        }

        if (result.length == 0) {
             result.push(setupNode(key_chain,value));
        }
   }

   return result
}
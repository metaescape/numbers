/*
abstraction layer for list and string operations
*/

function head(list) {
  return list[0];
}

function tail(list) {
  return list[1];
}

function is_null(x) {
  return x === null;
}

function pair(x, y) {
  return [x, y];
}

function set_head(pair, value) {
  pair[0] = value;
}

function set_tail(pair, value) {
  pair[1] = value;
}

function list(...elements) {
  return elements.length === 0
    ? null
    : pair(elements[0], list(...elements.slice(1)));
}

console.log(list(1, 2, 3));

function for_each(fun, items) {
  if (is_null(items)) {
    return undefined;
  } else {
    fun(head(items));
    return for_each(fun, tail(items));
  }
}

function error(message) {
  throw new Error(message);
}

function lookup(key, table) {
  const record = assoc(key, tail(table));
  return is_undefined(record) ? undefined : tail(record);
}

function is_pair(x) {
  return Array.isArray(x);
}

console.assert(is_pair(list(1, 2, 3)));

function is_number(x) {
  return typeof x === "number";
}

function is_boolean(x) {
  return typeof x === "boolean";
}

function is_string(ele) {
  return typeof ele === "string";
}

console.assert(is_number(3));
console.assert(is_boolean(3 > 2));
console.assert(is_string("xsd"));

function is_undefined(x) {
  return x === undefined;
}

function equal(xs, ys) {
  return is_pair(xs)
    ? is_pair(ys) && equal(head(xs), head(ys)) && equal(tail(xs), tail(ys))
    : is_null(xs)
    ? is_null(ys)
    : is_number(xs)
    ? is_number(ys) && xs === ys
    : is_boolean(xs)
    ? is_boolean(ys) && ((xs && ys) || (!xs && !ys))
    : is_string(xs)
    ? is_string(ys) && xs === ys
    : is_undefined(xs)
    ? is_undefined(ys)
    : // we know now that xs is a function
      is_function(ys) && xs === ys;
}

function append(list1, list2) {
  return is_null(list1) ? list2 : pair(head(list1), append(tail(list1), list2));
}

function assoc(key, records) {
  return is_null(records)
    ? undefined
    : equal(key, head(head(records)))
    ? head(records)
    : assoc(key, tail(records));
}

function is_tagged_list(component, the_tag) {
  return is_pair(component) && head(component) === the_tag;
}

function map(fun, items) {
  return is_null(items) ? null : pair(fun(head(items)), map(fun, tail(items)));
}

/*
abstraction layer for instrution extraction
*/
function make_label_entry(label_name, insts) {
  return pair(label_name, insts);
}

function make_inst(inst_controller_instruction) {
  return pair(inst_controller_instruction, null);
}

function inst_controller_instruction(inst) {
  return head(inst);
}

function set_inst_execution_fun(inst, fun) {
  set_tail(inst, fun);
}

function inst_execution_fun(inst) {
  return tail(inst);
}

/*
assemble generator format:

// assignment and control flow
assign(register-name, reg(register-name))
assign(register-name, constant(constant-value))
assign(register-name, list(op(operation-name), input1, ..., inputN))
perform(list(op(operation-name), input1, ..., inputN))
test(list(op(operation-name), input1, ..., inputN))
branch(label(label-name))
go_to(label(label-name))

// register addressing
assign(register-name, label(label-name))
go_to(reg(register-name))

// stack operations
save(register-name)
restore(register-name)
*/
function extract_labels(controller, receive) {
  return is_null(controller)
    ? receive(null, null)
    : extract_labels(tail(controller), (insts, labels) => {
        const next_element = head(controller);
        return is_string(next_element)
          ? receive(insts, pair(make_label_entry(next_element, insts), labels))
          : receive(pair(make_inst(next_element), insts), labels);
      });
}

function lookup_label(labels, label_name) {
  const val = assoc(label_name, labels);
  return is_undefined(val)
    ? error(label_name, "undefined label -- assemble")
    : tail(val);
}
/* assemble code*/

function test(condition) {
  return list("test", condition);
}

function op(name) {
  return list("op", name);
}

function branch(label) {
  return list("branch", label);
}

function reg(name) {
  return list("reg", name);
}

function constant(value) {
  return list("constant", value);
}

function label(name) {
  return list("label", name);
}

function assign(register_name, source) {
  return list("assign", register_name, source);
}

function go_to(label) {
  return list("go_to", label);
}

const gcd_assemble = list(
  "test_b",
  test(list(op("="), reg("b"), constant(0))),
  branch(label("gcd_done")),
  assign("t", list(op("rem"), reg("a"), reg("b"))),
  assign("a", reg("b")),
  assign("b", reg("t")),
  go_to(label("test_b")),
  "gcd_done"
);

function test_extract_labels() {
  let controller = list("start");
  extract_labels(controller, (insts, labels) => console.log(insts, labels));
}
test_extract_labels();

function test_extract_labels_from_gcd() {
  extract_labels(gcd_assemble, (insts, labels) => console.log(insts, labels));
}

test_extract_labels_from_gcd();

/*
assembler 
*/
function assemble(controller, machine) {
  return extract_labels(controller, (insts, labels) => {
    update_insts(insts, labels, machine);
    console.log(`labels after process >>>> ${labels}`);
    return insts;
  });
}

/*
update_insts need the implementation of machine
*/

// registers are the memory or state of the machine
function make_register(name) {
  let contents = "*unassigned*";
  function dispatch(message) {
    return message === "get"
      ? contents
      : message === "set"
      ? (value) => (contents = value)
      : error(message, "Unknown request -- make_register");
  }
  return dispatch;
}

function get_contents(register) {
  return register("get");
}

function set_contents(register, value) {
  return register("set")(value);
}

function get_register(machine, reg_name) {
  return machine("get_register")(reg_name);
}

// inorder to make arbitrary number of function calls, we nee a stack
function make_stack() {
  let stack = null;
  function push(value) {
    stack = pair(value, stack);
    return "done";
  }
  function pop() {
    if (is_null(stack)) {
      return error("Empty stack -- pop");
    } else {
      const top = head(stack);
      stack = tail(stack);
      return top;
    }
  }
  function initialize() {
    stack = null;
    return "done";
  }
  function dispatch(message) {
    return message === "push"
      ? push
      : message === "pop"
      ? pop()
      : message === "initialize"
      ? initialize()
      : error(message, "Unknown request -- stack");
  }
  return dispatch;
}

function pop(stack) {
  return stack("pop");
}

function push(stack, value) {
  return stack("push")(value);
}

// now we can define the machine

function make_new_machine() {
  const pc = make_register("pc");
  const flag = make_register("flag");
  const stack = make_stack();
  let the_instruction_sequence = null;

  // only one default operation: initialize_stack
  let the_ops = list(list("initialize_stack", () => stack("initialize")));

  let register_table = list(list("pc", pc), list("flag", flag));

  function allocate_register(name) {
    if (is_undefined(assoc(name, register_table))) {
      register_table = pair(list(name, make_register(name)), register_table);
    } else {
      error(name, "multiply defined register");
    }
    return "register allocated";
  }
  function lookup_register(name) {
    const val = assoc(name, register_table);
    return is_undefined(val)
      ? error(name, "unknown register")
      : head(tail(val));
  }

  function execute() {
    const insts = get_contents(pc);
    console.log(insts);
    console.log("---");
    console.log(get_contents(lookup_register("a")));
    if (is_null(insts)) {
      return "done";
    } else {
      inst_execution_fun(head(insts))();
      return execute();
    }
  }

  function dispatch(message) {
    function start() {
      set_contents(pc, the_instruction_sequence);
      return execute();
    }
    return message === "start"
      ? start()
      : message === "install_instruction_sequence"
      ? (seq) => {
          the_instruction_sequence = seq;
        }
      : message === "allocate_register"
      ? allocate_register
      : message === "get_register"
      ? lookup_register
      : message === "install_operations"
      ? (ops) => {
          the_ops = append(the_ops, ops);
        }
      : message === "stack"
      ? stack
      : message === "operations"
      ? the_ops
      : error(message, "unknown request -- machine");
  }
  return dispatch;
}

function make_machine(register_names, ops, controller) {
  const machine = make_new_machine();
  for_each(
    (register_name) => machine("allocate_register")(register_name),
    register_names
  );
  machine("install_operations")(ops);
  machine("install_instruction_sequence")(assemble(controller, machine));
  return machine;
}

function start(machine) {
  return machine("start");
}
function get_register_contents(machine, register_name) {
  return get_contents(get_register(machine, register_name));
}
function set_register_contents(machine, register_name, value) {
  set_contents(get_register(machine, register_name), value);
  return "done";
}

// now we can define the `machine code`, this is the js function that will be called by the machine

function make_execution_function(inst, labels, machine, pc, flag, stack, ops) {
  const inst_type = type(inst);
  return inst_type === "assign"
    ? make_assign_ef(inst, machine, labels, ops, pc)
    : inst_type === "test"
    ? make_test_ef(inst, machine, labels, ops, flag, pc)
    : inst_type === "branch"
    ? make_branch_ef(inst, machine, labels, flag, pc)
    : inst_type === "go_to"
    ? make_go_to_ef(inst, machine, labels, pc)
    : inst_type === "save"
    ? make_save_ef(inst, machine, stack, pc)
    : inst_type === "restore"
    ? make_restore_ef(inst, machine, stack, pc)
    : inst_type === "perform"
    ? make_perform_ef(inst, machine, labels, ops, pc)
    : error(inst, "unknown instruction type -- assemble");
}

// utils functions
function type(instruction) {
  return head(instruction);
}

// start from save and restore, these are the simplest instructions
function make_save_ef(inst, machine, stack, pc) {
  const reg = get_register(machine, stack_inst_reg_name(inst));
  return () => {
    push(stack, get_contents(reg));
    advance_pc(pc);
  };
}

function stack_inst_reg_name(inst) {
  return head(tail(inst));
}

function make_restore_ef(inst, machine, stack, pc) {
  const reg = get_register(machine, stack_inst_reg_name(inst));
  return () => {
    set_contents(reg, pop(stack));
    advance_pc(pc);
  };
}
//  then define the machine code of branch and go_to
function make_branch_ef(inst, machine, labels, flag, pc) {
  const dest = branch_dest(inst);

  if (is_label_exp(dest)) {
    const insts = lookup_label(labels, label_exp_label(dest));
    return () => {
      if (get_contents(flag)) {
        set_contents(pc, insts);
        console.log(`branch here --->>> ${insts}`);
      } else {
        advance_pc(pc);
      }
    };
  } else {
    error(inst, "bad branch instruction -- assemble");
  }
}

function is_label_exp(exp) {
  return is_tagged_list(exp, "label");
}

function label_exp_label(exp) {
  return head(tail(exp));
}

function branch_dest(branch_instruction) {
  return head(tail(branch_instruction));
}

function make_go_to_ef(inst, machine, labels, pc) {
  const dest = go_to_dest(inst);
  if (is_label_exp(dest)) {
    const insts = lookup_label(labels, label_exp_label(dest));
    return () => set_contents(pc, insts);
  } else if (is_register_exp(dest)) {
    const reg = get_register(machine, register_exp_reg(dest));
    return () => set_contents(pc, get_contents(reg));
  } else {
    error(inst, "bad go_to instruction -- assemble");
  }
}

function go_to_dest(go_to_instruction) {
  return head(tail(go_to_instruction));
}

function register_exp_reg(exp) {
  return head(tail(exp));
}

// define the assemble code and machine code of perform

function perform(action) {
  return list("perform", action);
}

function perform_action(perform_instruction) {
  return head(tail(perform_instruction));
}

function make_perform_ef(inst, machine, labels, operations, pc) {
  const action = perform_action(inst);
  if (is_operation_exp(action)) {
    const action_fun = make_operation_exp_ef(
      action,
      machine,
      labels,
      operations
    );
    return () => {
      action_fun();
      advance_pc(pc);
    };
  } else {
    error(inst, "bad perform instruction -- assemble");
  }
}

function is_operation_exp(exp) {
  return is_pair(exp) && is_tagged_list(head(exp), "op");
}

function make_operation_exp_ef(exp, machine, labels, operations) {
  const op = lookup_prim(operation_exp_op(exp), operations);
  const afuns = map(
    (e) => make_primitive_exp_ef(e, machine, labels),
    operation_exp_operands(exp)
  );
  return () =>
    apply_in_underlying_javascript(
      op,
      map((f) => f(), afuns)
    );
}

function lookup_prim(symbol, operations) {
  const val = assoc(symbol, operations);
  return is_undefined(val)
    ? error(symbol, "unknown operation -- assemble")
    : head(tail(val));
}

function operation_exp_op(op_exp) {
  return head(tail(head(op_exp)));
}

function operation_exp_operands(op_exp) {
  return tail(op_exp);
}

function make_primitive_exp_ef(exp, machine, labels) {
  if (is_constant_exp(exp)) {
    const c = constant_exp_value(exp);
    return () => c;
  } else if (is_label_exp(exp)) {
    const insts = lookup_label(labels, label_exp_label(exp));
    return () => insts;
  } else if (is_register_exp(exp)) {
    const r = get_register(machine, register_exp_reg(exp));
    return () => get_contents(r);
  } else {
    error(exp, "unknown expression type -- assemble");
  }
}

function is_constant_exp(exp) {
  return is_tagged_list(exp, "constant");
}

function constant_exp_value(exp) {
  return head(tail(exp));
}

function is_register_exp(exp) {
  return is_tagged_list(exp, "reg");
}

function apply_in_underlying_javascript(prim, arglist) {
  const arg_vector = [];
  let i = 0;
  while (!is_null(arglist)) {
    arg_vector[i] = head(arglist);
    i = i + 1;
    arglist = tail(arglist);
  }
  return prim.apply(prim, arg_vector);
}

// define the machine code of assign

function make_assign_ef(inst, machine, labels, operations, pc) {
  const target = get_register(machine, assign_reg_name(inst));
  const value_exp = assign_value_exp(inst);

  const value_fun = is_operation_exp(value_exp)
    ? make_operation_exp_ef(value_exp, machine, labels, operations)
    : make_primitive_exp_ef(value_exp, machine, labels);
  return () => {
    set_contents(target, value_fun());
    advance_pc(pc);
  };
}

function assign_reg_name(assign_instruction) {
  return head(tail(assign_instruction));
}

function assign_value_exp(assign_instruction) {
  return head(tail(tail(assign_instruction)));
}

function advance_pc(pc) {
  set_contents(pc, tail(get_contents(pc)));
}

// define the machine code of test
function make_test_ef(inst, machine, labels, operations, flag, pc) {
  const condition = test_condition(inst);
  if (is_operation_exp(condition)) {
    const condition_fun = make_operation_exp_ef(
      condition,
      machine,
      labels,
      operations
    );
    return () => {
      set_contents(flag, condition_fun());
      advance_pc(pc);
    };
  } else {
    error(inst, "bad test instruction -- assemble");
  }
}

function test_condition(test_instruction) {
  return head(tail(test_instruction));
}

// finally we can define the update_insts function
function update_insts(insts, labels, machine) {
  const pc = get_register(machine, "pc");
  const flag = get_register(machine, "flag");
  const stack = machine("stack");
  const ops = machine("operations");
  console.log(`labels before process : ${labels}`);
  return for_each(
    (inst) =>
      set_inst_execution_fun(
        inst,
        make_execution_function(
          inst_controller_instruction(inst),
          labels,
          machine,
          pc,
          flag,
          stack,
          ops
        )
      ),
    insts
  );
}

// now we have the complete machine, we can test it with assemble codes

const gcd_machine = make_machine(
  list("a", "b", "t"),
  list(
    list("rem", (a, b) => a % b),
    list("=", (a, b) => a === b)
  ),
  list(
    assign("a", constant(26)),
    assign("b", constant(13)),
    "test_b",
    test(list(op("="), reg("b"), constant(0))),
    branch(label("gcd_done")),
    assign("t", list(op("rem"), reg("a"), reg("b"))),
    assign("a", reg("b")),
    assign("b", reg("t")),
    go_to(label("test_b")),
    "gcd_done",
    assign("b", constant(100))
  )
);

start(gcd_machine);

// test for recursive exponentiation
/*

Figure 5.11 A recursive factorial machine. controller:

  list(      
    assign("continue", label("fact_done")),
    "fact_loop",
      test(list(op("="), reg("n"), constant(1))),
      branch(label("base_case")),
      save("continue"),
      save("n"),
      assign("n", list(op("-"), reg("n"), constant(1))),
      assign("continue", label("after_fact")),
      go_to(label("fact_loop")),
    "after_fact",
      restore("n"),
      restore("continue"),
      assign("val", list(op("*"), reg("n"), reg("val"))),  
      go_to(reg("continue")),  
    "base_case",
      assign("val", constant(1)), 
      go_to(reg("continue")), 
    "fact_done"))
*/

/*


*/

/*
Recursive exponentiation:

function expt(b, n) {
    return n === 0
           ? 1
           : b * expt(b, n - 1);
} 

Iterative exponentiation:

function expt(b, n) {	  
    function expt_iter(counter, product) {
        return counter === 0
               ? product
               : expt_iter(counter - 1, b * product);
    }
    return expt_iter(n, 1);
}

*/

function runCode() {
  // 获取代码块的内容
  var codeContent = document.getElementById("code").innerText;

  // 运行代码并显示结果
  try {
    read_and_parse(codeContent);
  } catch (error) {
    console.error(error);
    document.getElementById("output").innerText = "Error: " + error.message;
  }
}

class Apply {
  constructor(first, second = null) {
    this.first = first;
    this.second = second;
  }

  js() {
    let first = this.first;
    let second = this.second;
    let res = typeof first === "string" ? `${first}` : `${first.js()}`;
    while (second !== null) {
      first = second.first;
      if (typeof first === "string") {
        res = res.length > 1 ? `(${res})(${first})` : `${res}(${first})`;
      } else {
        res =
          res.length > 1 ? `(${res})(${first.js()})` : `${res}(${first.js()})`;
      }
      second = second.second;
    }
    return res;
  }

  toString() {
    let first = this.first;
    let second = this.second;
    let res =
      first instanceof Lambda && second !== null ? `(${first})` : `${first}`;
    while (second !== null) {
      first = second instanceof Apply ? second.first : second;
      res = typeof first === "string" ? `${res}${first}` : `${res}(${first})`;
      second = second instanceof Apply ? second.second : null;
    }
    return res;
  }
}

class Lambda {
  constructor(arg, body) {
    this.arg = arg;
    this.body = body;
  }

  js() {
    return `(${this.arg})=> (${this.body.js()})`;
  }

  toString() {
    let exp = this;
    let res = "λ";
    while (exp.body instanceof Lambda) {
      res += exp.arg;
      exp = exp.body;
    }
    res += `${exp.arg}.${exp.body}`;
    return res;
  }
}

function tree_equal(ast1, ast2) {
  if (ast1 instanceof Apply && ast2 instanceof Apply) {
    return (
      tree_equal(ast1.first, ast2.first) && tree_equal(ast1.second, ast2.second)
    );
  }
  if (ast1 instanceof Lambda && ast2 instanceof Lambda) {
    return ast1.arg === ast2.arg && tree_equal(ast1.body, ast2.body);
  }
  return ast1 === ast2;
}

class LLLparser {
  constructor(s) {
    this.s = s.replace(/\s/g, "");
    this.i = 0;
  }

  parse_apply() {
    if (this.i === this.s.length || this.s[this.i] === ")") {
      return null;
    }
    if (this.s[this.i] === "(") {
      this.i += 1;
      const first = this.parse();
      if (this.s[this.i] !== ")") {
        throw new Error("parentheses not match");
      }
      this.i += 1;
      return new Apply(first, this.parse_apply());
    } else {
      const first = this.s[this.i];
      this.i += 1;
      return new Apply(first, this.parse_apply());
    }
  }

  parse_lambda() {
    if (this.s[this.i] === ".") {
      this.i += 1;
      return this.parse();
    }
    const varName = this.s[this.i];
    this.i += 1;
    return new Lambda(varName, this.parse_lambda());
  }

  parse() {
    if (this.s[this.i] === "(" && new Set(["L", "λ"]).has(this.s[this.i + 1])) {
      this.i += 2;
      const lmb = this.parse_lambda();
      if (this.s[this.i] !== ")") {
        throw new Error("parentheses not match");
      }
      this.i += 1;
      return new Apply(lmb, this.parse_apply());
    }

    if (new Set(["L", "λ"]).has(this.s[this.i])) {
      this.i += 1;
      return this.parse_lambda();
    }
    return this.parse_apply();
  }
}

function read_and_parse(string) {
  const expressions_str = string.split("\n");

  const subst_map = {};
  for (let exp of expressions_str) {
    exp = exp.trim();
    if (exp === "" || exp.startsWith(";") || exp.startsWith("#")) {
      continue;
    }
    if (exp.includes("=")) {
      const [key, value] = exp.split("=");
      const parser = new LLLparser(preprocess(value.trim(), subst_map));
      const ast = parser.parse();
      subst_map[key.trim()] =
        ast instanceof Apply ? `${evaluate(ast)}` : `${ast}`;
      continue;
    }
    setTimeout(() => {
      processOneLine(exp, subst_map);
    }, 0);
  }
}

function processOneLine(exp, subst_map) {
  document.getElementById("output").innerText += `\n${exp} -> `;
  const exp_ = preprocess(exp.trim(), subst_map);
  let ast = new LLLparser(exp_).parse();
  if (numerical(exp)) {
    let res = evaluate(ast);
    document.getElementById("output").innerText += `${decode(res)}: ${res}`;
  } else {
    const res = evaluate(ast);
    document.getElementById("output").innerText += `${res}`;
  }
}

function numerical(exp) {
  const numericalOps = ["FACT", "PRED", "ADD", "MUL", "ACC", "EXP", "ISZERO"];
  return numericalOps.some((op) => exp.includes(op));
}

class VariableGenerator {
  constructor(vars = new Set()) {
    this.vars = vars;
    this.hub = this.createHub();
  }

  *createHub() {
    const base = "abcdefghijklmnopqrstuvwxyz";
    // 生成单个字母的变量
    for (let char of base) {
      yield char;
    }
    // 生成带数字的变量
    for (let char of base) {
      for (let i = 0; i < 100; i++) {
        yield char + i;
      }
    }
  }

  next() {
    let result = this.hub.next();
    while (!result.done) {
      let ele = result.value;
      if (!this.vars.has(ele)) {
        this.vars.add(ele);
        return ele;
      }
      result = this.hub.next();
    }
    throw new Error("no more variables");
  }
}

function get_variables(exp) {
  if (exp instanceof Apply) {
    return new Set([...get_variables(exp.first), ...get_variables(exp.second)]);
  }
  if (exp instanceof Lambda) {
    return new Set([exp.arg, ...get_variables(exp.body)]);
  }
  if (typeof exp === "string") {
    return new Set([exp]);
  }
  return new Set();
}

function preprocess(exp, subst_map) {
  const subst_lst = Object.entries(subst_map).sort((a, b) => {
    return b[0].length - a[0].length || a[0].localeCompare(b[0]);
  });
  for (const [key, value] of subst_lst) {
    let processedValue = value;
    if (!value.startsWith("(")) {
      processedValue = `(${value})`;
    }
    const regex = new RegExp(key, "g");
    exp = exp.replace(regex, processedValue);
  }
  return exp;
}

function alpha_conv(exp, varName, generator) {
  if (!(exp instanceof Lambda) || varName !== exp.arg) {
    return exp;
  }

  const newVar = generator.next();

  function _alpha(exp) {
    if (exp instanceof Apply) {
      return new Apply(_alpha(exp.first), _alpha(exp.second));
    }
    if (exp instanceof Lambda) {
      if (exp.arg === varName) {
        return exp;
      }
      return new Lambda(exp.arg, _alpha(exp.body));
    }
    if (exp === varName) {
      return newVar;
    }
    return exp;
  }

  return new Lambda(newVar, _alpha(exp.body));
}

function beta_reduce(exp, env = {}, generator) {
  if (typeof exp === "string") {
    return env[exp] || exp;
  }

  if (exp instanceof Lambda) {
    if (Object.keys(env).length > 0) {
      const key = Object.keys(env)[0];
      const allVariables = get_variables(env[key]);
      if (allVariables.has(exp.arg) && get_variables(exp.body).has(key)) {
        exp = alpha_conv(exp, exp.arg, generator);
      }
      env = key == exp.arg ? {} : env;
    }
    return new Lambda(exp.arg, beta_reduce(exp.body, env, generator));
  }

  if (exp instanceof Apply) {
    if (Object.keys(env).length > 0) {
      return new Apply(
        beta_reduce(exp.first, env, generator),
        beta_reduce(exp.second, env, generator)
      );
    }

    if (exp.first instanceof Lambda) {
      if (exp.second === null) {
        return exp.first;
      }

      let lam = exp.first;
      let value = exp.second;
      let remain = null;

      if (exp.second instanceof Apply) {
        value = exp.second.first;
        remain = exp.second.second;
      }

      env = { [lam.arg]: value };
      return new Apply(beta_reduce(lam.body, env, generator), remain);
    }
    return reduce_list(exp, env, generator);
  }
  return exp;
}

function reduce_list(exp, env, generator) {
  if (!(exp instanceof Apply)) {
    return beta_reduce(exp, env, generator);
  }

  return new Apply(
    beta_reduce(exp.first, env, generator),
    reduce_list(exp.second, env, generator)
  );
}

function evaluate(ast, max_step = 2000) {
  for (let i = 0; i < max_step; i++) {
    const generator = new VariableGenerator(get_variables(ast));
    let ast_after = beta_reduce(ast, {}, generator);
    if (tree_equal(ast, ast_after)) {
      return ast;
    }
    ast = ast_after;
  }
  return ast;
}

function decode(lam) {
  function inc(x) {
    return x + 1;
  }

  const exp = eval(lam.js());
  try {
    return exp(1)(0);
  } catch {
    return exp(inc)(0);
  }
}

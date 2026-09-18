```
Control Structure

体：
System
Sub System
ECU
Component

用：
State Variable
    ↓
Condition = State Variable 在相关时刻/窗口的 Snapshot
    ↓
Arbitration / Decision
    ↓
Request / Command
    ↓
Execution
    ↓
Feedback / Result
```

诊断定位要定位到“体”。这样一个层级：

状态机与部件s（传感器是部件的数字化体现，部件s是复数的意思）
  
部件传感器(【体】部件的状态感知者，部件的数字化抽象代表，通常是一组) -输出-> 变量Vars
  ｜
输出形成
  ↓ 
当前稳态图（变量Vars在一个时间点snapshot的稳态,多种状态）-给到-> 控制（某个或者多个控制器【体】）
                                                            ｜
                                                仲裁（变量变化，计算，是否达到跃迁条件）--yes--> 下一个状态图 --x
                                                            ｜
                                                            no
                                                            ｜
                                                        继续稳态



故障原因定位（功能诊断）
      
现象（功能不可用）--有DTC-->
 |
无DTC


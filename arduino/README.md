# ADCs

<img align="left" src="https://img.shields.io/badge/Environment-Arduino-blue"><img align="left" src="https://img.shields.io/badge/Estimated_duration-2 h-green"></br>

[ADC or _Analog-to-Digital Converter_](https://en.wikipedia.org/wiki/Analog-to-digital_converter) is a fundamental peripheral in [AMS (_Analog Mixed Signal_)](https://en.wikipedia.org/wiki/Mixed-signal_integrated_circuit) circuits or mixed-signal circuits. With the **ADC**, we will be able to **convert a continuous voltage signal into a digital signal** by performing a **discretization** and **quantification** of the **continuous signal**.

![](/.github/images/chart-conversion.png)

> [!NOTE]
> In the image, discretization and quantification of an analog voltage signal. Characteristics of the analog signal: amplitude 3.3 V<sub>p-p</sub>, frequency of 1 Hz, and offset of 1.65 V. Characteristics of the conversion: 3-bit resolution, 3.3 V reference voltage, and sampling rate of 25 Sps.

Let’s quickly review ADCs, remembering what reference voltage, [resolution bits](https://en.wikipedia.org/wiki/Analog-to-digital_converter#Resolution), and [_sampling rate_](<https://en.wikipedia.org/wiki/Sampling_(signal_processing)#Sampling_rate>) are:

- **Resolution bits:** this is the number of bits the ADC has to generate a digital value from an analog signal value. For example, if an ADC has 10 bits, the ADC can generate up to 2<sup>10</sup> values (from 0 to 1023 in decimal). Another example, as shown in the image, if an ADC has 3 bits, it can generate up to 2<sup>3</sup> values (from 0 to 7 in decimal). Along with the reference voltage, the number of bits of an ADC sets the resolution of the ADC.
- **Reference voltage:** a fixed reference voltage value (V<sub>ref</sub>) used to compare it with the input analog signal (V<sub>signal</sub>) being quantified. For example, assuming a 10-bit ADC, if the input signal is equal to the reference voltage, the ADC will output 1023, the highest value. If the input signal is one-third of the reference voltage, the ADC will output 341 (one-third of 1023). The conversion formula would be:

```math
\text{ADC}_{\text{value}}=\frac{\text{V}_{\text{signal}}}{\text{V}_{\text{ref}}}(2^{\text{bits}}-1)
```

- **_Sampling rate_:** the number of samples per second we take from the analog signal. It can be given in Hertz or Sps (_Samples per second_). Here, we need to remember to apply the [Nyquist criterion](https://en.wikipedia.org/wiki/Nyquist_rate).

There you go. Summarized ADCs in four and a half paragraphs 🤣 Now, seriously, ADCs are a whole world on their own, and here we will only see how to operate them with the microcontroller. With the basic information we've covered, that will be enough.

Before getting into the subject, we’ll see that **Arduino’s offering for working with ADCs is very basic**. More advanced things could be done and Arduino could be twisted a bit, but the complexity level to do that would make direct register-level work more efficient. Therefore, **in this practice, we will incorporate a teamworkflow for the first time** in the course. As a challenge, we will make a common program/project between you and your partner. _Let's go!_

## Objectives

- Introduction to ADCs in Arduino.
- Combination of _timers_ and ADC in Arduino for fixed _sampling rates_.
- Introduction to Git-based _workflows_ for team collaboration.

## Procedure

### Conversion with a voltage divider

We will see how to read an analog signal from a voltage divider implemented with a joystick. The first thing we will do is learn how to connect this joystick.

#### Joystick connection

Do you like your computer? Would you like it to last many years? Well, **make sure to follow these steps carefully** since we will be connecting the joystick to the EVB, which in turn is connected to your computer's USB port. If you cause a short circuit... 🔥 I'll leave it at that.

> [!NOTE]
> Actually, **the EVB has a safety system** that protects the USB port from potential short circuits. But the ideal and recommended approach is **not to tempt fate**.

With the EVB disconnected from the USB port, i.e., without power, we will connect the `GND` terminal to, oh, surprise, `GND` and the **`+5V` terminal to `3V3`** (careful, do not connect the `+5V` terminal to the `5V`...). The **_labels_ of the [_silkscreen_](https://en.wikipedia.org/wiki/Printed_circuit_board#Silkscreen_printing)** on the PCB show where you can find these nodes. With this, we will be creating a **voltage divider that we will control with the position of the joystick**. The **variable terminal** (which in this case would be either `VRx` or `VRy`, depending on which joystick axis we want to read), the output of the divider, we **connect to `A0`**.

To better understand how the joystick works, a video is worth a thousand words, so here is an explanatory video.

https://github.com/user-attachments/assets/148df222-a7db-4a70-9eee-cb4eb0f7e71b

> [!NOTE]
> I downloaded the video from YouTube and incorporated it into the repository to preserve it, but you can find the original video at the following [link](https://www.youtube.com/watch?v=UUlXBcakcdI). If you found the video useful, feel free to go to YouTube and give it a 👍

Now, connect the EVB to the USB port and we can go to the PlatformIO to program.

#### Workspace management and branch naming policy

This is the first repository we share as a team. If we were all asked to create a branch named `analog-read`, the first person to create it would have no problem, but any other member who later tried to create a branch with the same name would run into issues since it already exists in the repository. On the other hand, if that second member decided to use the existing branch, they would be working on the same development branch as their teammate, leading to conflicts and history inconsistencies.

To keep branches organized, we use a two-level folder structure. The **first level identifies the platform** the branch belongs to (`arduino` or `stm32cube`), and the **second level identifies the student** for individual developments. For individual developments, branch names follow the format `arduino/<username>/<branch-name>`, where `<username>` must be replaced with your GitHub username (you can find your username on your GitHub profile), and `<branch-name>` must be replaced with the indicated name. For example, if asked to create a branch named `arduino/<username>/analog-read`, I would use `arduino/TheAlbertDev/analog-read`. For team developments where branches are shared, use the format `arduino/<branch-name>` — that is, with the platform folder but without the `<username>/` sub-folder. For example, a shared branch named `arduino/develop`. The only exception to this policy is the `main` branch, which must be named exactly `main`.

This same convention applies to the STM32Cube part of the lab sessions, where all branches must be prefixed with `stm32cube/` instead. For example, individual branches would be `stm32cube/<username>/<branch-name>` and shared branches would be `stm32cube/<branch-name>`.

The same problem arises with workspaces. If everyone is asked to create an individual project named `challenge` in the workspace, the first member to merge their Pull Request would have no issue, but when a second member tried to merge theirs, conflicts would arise because those files already exist in the `main` branch (merged by the first member). The solution? We follow the same approach as with branches. Inside the `workspace` folder, each person creates a subfolder with their GitHub username, and places their projects inside it. Shared projects — I will remind you of this again when we start those developments — must be placed in a folder named `shared` inside the `workspace` folder. My own projects, for example, would go in `workspace/TheAlbertDev`.

> [!WARNING]
> The automated tests will use the username indicated in the branch names or workspace folders, so make sure to use your exact GitHub username.

#### Reading an analog signal

Let's get to it. Create a branch named `arduino/<username>/analog-read` from the `main` branch and create a PlatformIO project named `analog-read` in the `arduino/workspace/<username>` folder.

All right. To **read an analog signal in Arduino**, simply use the **`analogRead`** function, specifying the pin where the signal to be read is connected. That's it. Nothing else. No need to configure the pin or anything. We can just collect and head home.

No, no, no! Just kidding. Let's play around a bit since working with ADCs in Arduino is so easy.

In the program, **we will create a numeric variable of type `uint32_t`** called `adcVal` to store the value resulting from the ADC conversion. The program will look like this:

```c++
#include <Arduino.h>

uint32_t adcVal = 0; // variable to store the conversion

void setup()
{
  // put your setup code here, to run once:
}

void loop()
{
  // put your main code here, to run repeatedly:

  adcVal = analogRead(A0); // read the conversion value
}
```

We build and upload the program. Does it work? No idea 🤣 Let's debug the application. Start a debug session from the Run and Debug tab.

![](/.github/images/platformio-debug.png)

The code execution, as usual, will pause at the start of the application. This first stop occurs in a `main.cpp` file that is not ours. You are looking at the file that PlatformIO automatically generates, which, if you look closely, calls our `setup` and `loop` functions.

![](/.github/images/platformio-debug-first-breakpoint.png)

All right. Open our `main.cpp` file in the `src` folder and set a breakpoint on the line that uses the `analogRead` instruction. Remember: to create a breakpoint, simply click to the left of the line number.

![](/.github/images/platformio-debug-set-breakpoint.png)

Finally, click the Play icon in the debug session control bar to continue code execution.

![](/.github/images/platformio-debug-controls.png)

The code will run until the line where we placed the breakpoint. This highlighted line has not been executed yet. Therefore, the value of the variable `adcVal` is still 0. We can see its value in the global variables section (because we declared it as a global variable; otherwise we would look in the locals section) within the Variables panel, or we can add it to the Watch panel by typing the variable name.

![](/.github/images/platformio-debug-variables.png)

Resume the debug session by clicking the Play icon. The `analogRead` instruction will execute and the program will stop at the breakpoint again. This time we can see that the variable `adcVal` has been updated with the digital value of the converted analog signal.

Resume the debug session several times while moving the joystick and check how the value of `adcVal` changes.

Once you are done playing, stop the debug session by clicking the Stop button. If everything works as expected, make a commit, push your changes, and create a Pull Request to the main branch. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request.

#### Serial communication

Honestly, it is a pain to keep clicking Play just to check that the ADC value is being obtained correctly. And not very appealing either... Wouldn't it be cool to see the captured values — that is, the signal — in a graph? Well, that is exactly what we are going to do. To that end, we will have a first introduction to serial communication.

To do so, create a branch named `arduino/<username>/analog-serial` from `main` and create a project named `analog-serial`.

**We will cover it in detail in later sessions**, but basically what we will do is **establish serial communication between our computer and the microcontroller** and make the microcontroller send the ADC conversion values so we can see that everything is working.

Until we get to that point in later sessions, starting from a `main.cpp` that contains the same code as in the previous project (`analog-read`), simply follow these steps.

1. We initialize the serial communication in the `setup` function with the instruction `Serial.begin(9600)`, where 9600, as we will see in another session, is the **_baudrate_**.
2. We use the `Serial.println` function to **send a text/number** followed by **a carriage return** so that the numbers we send appear on separate lines in the computer.

The code will look like this:

```c++
#include <Arduino.h>

uint32_t adcVal = 0; // variable to store the conversion

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // configure serial communication
}

void loop()
{
  // put your main code here, to run repeatedly:

  adcVal = analogRead(A0); // read the conversion value
  Serial.println(adcVal);  // send the conversion value to the PC
}
```

We build, upload, and... Still see nothing 🤨

We need to **open the serial terminal** to see the data the microcontroller is sending us. To do this, go to the PlatformIO tab and select Monitor. A terminal will open where we will see numbers being spat out at full speed.

![](/.github/images/platformio-serial.png)

Trust me: those are the values of the variable `adcVal`. What is happening is that the microcontroller is running at full speed.

If we move the joystick, we will see that the values in the terminal vary between 0 and 1023.

As we can see, the terminal is extremely useful, but to see a value that updates continuously... it can be impractical. We can install a second tool in PlatformIO. **Close the serial terminal** by clicking the trash can icon. Then, go to the PlatformIO tab and click on Serial & UDP Plotter in the Miscellaneous section.

![](/.github/images/platformio-open-serial-plotter.png)

This will take you to the Extensions tab, showing an extension called teleplot. Install it. Once installed, go back to the `main.cpp` file and add the following lines:

```diff
#include <Arduino.h>

uint32_t adcVal = 0; // variable to store the conversion

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // configure serial communication
}

void loop()
{
  // put your main code here, to run repeatedly:

  adcVal = analogRead(A0);  // read the conversion value
+ Serial.print(">adcVal:"); // send a string to the PC to identify the conversion value
+ Serial.println(adcVal);   // send the conversion value to the PC
}
```

Essentially, before sending the value of `adcVal` we send the label that identifies it. We do this by sending the label with `>` as a prefix and `:` as a suffix. Note that in this first send we use `print` and in the second `println`. The former sends the message without appending a newline, which `println` does.

All right. Save, build, and upload. Next, open teleplot. To do so, press the shortcut (<kbd>CTRL</kbd> or <kbd>⌘</kbd>)+<kbd>SHIFT</kbd>+<kbd>P</kbd>. In the input textbox that appears, type teleplot and press <kbd>ENTER</kbd>.

![](/.github/images/platformio-teleplot.png)

Teleplot opens and there we select the serial port of the device we want to connect to, which will be named COM<X>, where <X> is a number, select the baud rate, which is 9600, and click Open.

> [!NOTE]
> For users of Cupertino products or Linux, instead of COM<X>, the ports will appear in the style of `/dev/cu.usbmodem143103`. It may vary slightly, like the numbering, for example.

Once connected, we can finally see a graph with the values of `adcVal`! Play with the joystick and watch how the waveform changes.

![](/.github/images/platformio-waveform.png)

Ready to capture the signal from the other joystick axis? Of course you are, no way around it 😅 To do so, connect the remaining pin, `VRx` or `VRy`, to pin A1. Now, simply read that channel with `analogRead` and send it over the serial port. It would look like the following, where I have renamed the variables to match the joystick pins:

```c++
#include <Arduino.h>

uint32_t VRx = 0;
uint32_t VRy = 0;

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // configure serial communication
}

void loop()
{
  // put your main code here, to run repeatedly:

  VRx = analogRead(A0);  // read the conversion value
  VRy = analogRead(A1);  // read the conversion value
  Serial.print(">VRx:"); // send a string to the PC to identify the conversion value
  Serial.println(VRx);   // send the conversion value to the PC
  Serial.print(">VRy:"); // send a string to the PC to identify the conversion value
  Serial.println(VRy);   // send the conversion value to the PC

  Serial.print(">position:"); // send the position label to the PC
  Serial.print(VRx);          // send VRx value to the PC
  Serial.print(":");          // send separator to the PC
  Serial.print(VRy);          // send VRy value to the PC
  Serial.println("|xy");      // indicate end of position data
}
```

You will notice that, taking advantage of how extremely simple the code is, I also added the data to generate an X-Y plot that I called `position`.

![](/.github/images/platformio-xy-plot.png)

Check that it works correctly. If so, make a commit, push your changes, and create a Pull Request to the main branch. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request.

As you can see, it was quick. Now let's look at the challenge.

## Challenge: Control of the _sampling rate_

In applications where an analog signal is captured/converted, **it is very important to establish a known and stable _sampling rate_**. When coded like the previous program, we have no control over the sampling rate. If for some reason we added more code to the `loop` function (which would be the most normal), the conversion would happen when it hits the `analogRead` instruction, but all the code before or after in the `loop` function would have been executed first. This means we can't get a _sampling rate_ that we want, as we cannot determine how long it will take for the microprocessor to execute the rest of the instructions. For example, in the previous case, we can't say that we want a _sampling rate_ of 1 Sps.

We also can't guarantee that the _sampling rate_ will be constant since, if there is a conditional statement (`if-else`) or a loop with variable iterations, the execution time of the `loop` function code will differ each time. We need to ensure that the `analogRead` instruction is executed with a constant periodicity of our choice. Can you think of something? Yes. _Timers_.

Now, let's look at an example of a **project** with an **ADC conversion** at a **_constant sampling rate_ of 10 Sps**. Additionally, **we will enable and disable the conversion at will with the button**.

Remember: since this is a team project, we will create the project in a folder named `shared` inside the workspace, and branches use the `arduino/` platform prefix but no username sub-folder.

#### Basic _Workflow_ for teamwork

We will do this challenge in pairs. For the first time, we will work on an **Arduino project using more than one file**. **Each member will work on different files**. The **tasks are divided** between team member `A` and team member `B`.

Team member `A` will take care of the project creation and of the following files:

- `main.cpp`
- `adc.cpp`

Team member `B` will take care of the following files:

- `gpio.cpp`
- `timer.cpp`

Now, we will separate the workflow of both members into two distinct sections. Make sure to **complete your tasks**, but **it’s recommended that you also read your teammate’s section** to know what they’ve done.

Since member `A` is in charge of creating the project, member `B` must wait until the project has been created and pushed to the remote repository. The pressure is on, member `A`!

<details>
  <summary><h4>Workflow of member "A"</h4></summary>

##### Development Branch

The first thing we will do is create a branch named `arduino/develop` from the `main` branch. This branch will consolidate all the developments being made until they are complete. Once development is finished, a Pull Request to `main` will be required, as that is the branch containing the "final" versions, or those ready for production.

Once the `arduino/develop` branch is created, create a PlatformIO project named `challenge` (remember: inside a folder named `shared`). Once created, make a commit and push the changes to the remote repository so that member `B` can start their work. (Give them a heads-up — don't be mean...)

##### Development of `main.cpp`

Now let's start our actual work. First, we create a branch for our development so that nobody gets in our way (and we don't get in anyone else's). Create a branch named `arduino/member-a` from the `arduino/develop` branch. Once created, open the `main.cpp` file and, apart from initializing serial communication, we will call two functions that **initialize the GPIO and the _timer_**. _"But the `B` member does that!"_ He/she will implement it, we will just call the functions he/she has to make. These functions to initialize the GPIO and the _timer_ will be called `GPIO_Init` and `TIMER_Init`, respectively.

> [!NOTE]
> In a professional environment, the functions would be named this way because you and your colleague agreed on it, or because your supervisor or software architect told you so. The point is that both members have to use the same naming convention.

The code would look like this:

```c++
#include <Arduino.h>
#include "gpio.h"
#include "timer.h"

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // configure serial communication

  TIMER_Init(); // initialize the timer
  GPIO_Init();  // initialize the GPIO
}

void loop()
{
  // put your main code here, to run repeatedly:
}
```

We have completed the planned development for the `main.cpp` file. We will only initialize the indicated peripherals and won't do anything in the `loop` function, as we will handle everything with interrupts.

This would be a good time to **make a _commit_** and **_push_**.

##### Development of `adc.cpp`

Create a new file inside the `src` folder named `adc.cpp`. In this file, **we will create a function called `conversionADC`** that will be called by our partner from the _timer_.

> [!NOTE]
> Our partner will know the function is called `conversionADC` because that’s what we agreed on, or our superior or the software architect told us to.

In the file, we will start by creating a **macro** to refer to the pin we will use for the ADC. Then, we will **create two variables**: `valADC` and `onADC`. The first will store the **resulting value from the ADC conversion**, and the second will be used to configure the ADC as **off or on**. Notice that both variables are declared with the `static` keyword:

```c++
#include <Arduino.h>

#define ANALOG_PIN A0

static uint32_t valADC = 0; // variable to store the conversion value
static bool onADC = false;  // variable that tells us if the ADC is off or on

void setOnADC(bool state)
{
    onADC = state;
}

bool getOnADC(void)
{
    return onADC;
}

// perform a conversion if the ADC is on and send it via serial port
void conversionADC(void)
{

}
```

> [!NOTE]
> When `static` is applied to a **global variable** (i.e., a variable declared at file scope, outside any function), it **restricts the variable's visibility to the translation unit** — that is, to the `.cpp` file where it is declared. Without `static`, a global variable has _external linkage_ by default, meaning any other file could declare it with `extern` and access it directly. By marking `valADC` and `onADC` as `static`, we ensure they are **private to `adc.cpp`**: no other file can reach them. Instead, external code must go through the `setOnADC` and `getOnADC` functions we provide. This is the C equivalent of private class members, and it is good practice in modular C/C++ design.

We still need to implement the `conversionADC` function. In this function, we will check if the ADC is on or off, and if it is on, we will perform an ADC conversion and display it through the _Serial Plotter_. Our partner will control the value of `onADC` from the button's ISR by calling `setOnADC` and `getOnADC`. The final code will look like this:

```c++
#include <Arduino.h>

#define ANALOG_PIN A0

static uint32_t valADC = 0; // variable to store the conversion value
static bool onADC = false;  // variable that tells us if the ADC is off or on

void setOnADC(bool state)
{
    onADC = state;
}

bool getOnADC(void)
{
    return onADC;
}

// perform a conversion if the ADC is on and send it via serial port
void conversionADC(void)
{
    if (onADC) // if it is on
    {
        valADC = analogRead(ANALOG_PIN); // perform a conversion

        Serial.print(">valAdc:"); // send label for ADC value
        Serial.println(valADC);   // send the current ADC conversion value
    }
}
```

But we already know from previous sessions, when we created the `app.c` file with the `setup` and `loop` functions in STM32Cube: if we want the functions to be callable, we need to create a header file with their prototypes. Let's do it. Simply create a file named `adc.h` in the `include` folder and add the following:

```c++
#ifndef ADC_H_
#define ADC_H_

#include <stdbool.h>

void conversionADC(void);
void setOnADC(bool state);
bool getOnADC(void);

#endif /* ADC_H_ */
```

We save and make a **_commit_**. Also, make a **_push_** to upload the changes to the server.

##### _Pull Request_ and _Review_

Our work would have finished. Or almost. **There are two things missing**. First of all, **make a _Pull Request_ from this branch to `arduino/develop` and <u>importantly, set our partner `B` as the _reviewer_</u>**. He will review our code and, if it looks ok, either you or he can perform the merge to the develop branch. If it doesn't get the ok, you will need to address any requested changes, make the necessary modifications, commit and push the changes, and request a second review or _re-request_.

I have added some tests to check that everything is ok before merging. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request, but **wait for your mate approval!**

Your work doesn't end here, because now **you need to go to your partner's _Pull Request_**, **check that everything is ok**, and if so, approve the _Pull Request_. If you are not satisfied with his development, let him know and suggest changes. Once he applies them, approve the _Pull Request_ and either you or he should perform the merge to the develop branch.

I leave you a [link](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/reviewing-changes-in-pull-requests) to GitHub's help documentation where you can see in detail everything you can do during the _Pull Request_ review.

> [!NOTE]
> In this project, it doesn't matter who does the first _merge_ to the `arduino/develop` branch.

</details>

<details>
  <summary><h4>Workflow of member "B"</h4></summary>

##### Development Branch

The first step is to switch to the git branch named `arduino/develop` created by our mate. If it does not exist yet, give your teammate a nudge to hurry up.

Once on the branch, we can see that our teammate has created a project named `challenge` inside the `shared` folder. Open the project with PlatformIO.

##### Development of `gpio.cpp`

Now, from the `arduino/develop` branch, we will create a branch for our development so that nobody gets in our way (and we don't get in anyone else's). We will call this branch `arduino/member-b`.

Once done, go to the project and create a file named `gpio.cpp` in the `src` folder. In this file, we will **create two functions**: `GPIO_Init` and `toggleStateADC`. In the first function, we will **initialize the GPIO** (set mode to `INPUT` and configure an ISR), and the second function will be the **ISR that runs when the button is pressed**. Your teammate will call the first function, `GPIO_Init`, from the `setup` function in the `main.cpp` file.

> [!NOTE]
> Your teammate would know the names of your functions to call them because, in a professional environment, you both agreed on them or your supervisor or the software architect told you what to use. The point is, both team members need to use the same naming conventions.

We would also create a **macro** to make the code easier to read. The code would look like this:

```c++
#include <Arduino.h>

#define PUSH 23

// GPIO configuration
void GPIO_Init(void)
{
}

void toggleStateADC(void)
{
    // ISR for the BUTTON
}
```

In `GPIO_Init`, we configure the GPIO and its ISR.

```c++
#include <Arduino.h>

#define PUSH 23

void toggleStateADC(void);

// GPIO configuration
void GPIO_Init(void)
{

    pinMode(PUSH, INPUT); // configure PUSH as an input GPIO
    // add an interrupt to the PUSH pin for a transition from HIGH to LOW (falling)
    attachInterrupt(digitalPinToInterrupt(PUSH), toggleStateADC, FALLING);
}

void toggleStateADC(void)
{
    // ISR for the BUTTON
}
```

**In the ISR, we toggle the ADC state** by calling `setOnADC` and `getOnADC`, functions declared by our teammate in `adc.cpp`. `getOnADC` returns the current state, we negate it, and pass it to `setOnADC` — all without ever touching the `onADC` variable directly. You know the names of these functions because that's what you agreed on with them, or because your superior instructed you to name them that way. The code would look as follows:

```c++
#include <Arduino.h>
#include "adc.h"

#define PUSH 23

void toggleStateADC(void);

// GPIO configuration
void GPIO_Init(void)
{

    pinMode(PUSH, INPUT); // configure PUSH as an input GPIO
    // add an interrupt to the PUSH pin for a transition from HIGH to LOW (falling)
    attachInterrupt(digitalPinToInterrupt(PUSH), toggleStateADC, FALLING);
}

void toggleStateADC(void)
{
    // ISR for the BUTTON
    setOnADC(!getOnADC()); // toggle the state of the ADC
}
```

Notice how, since we are calling `setOnADC` and `getOnADC` from `adc.cpp`, we include the `adc.h` file, in which we declare those functions.

We also want others to be able to call the function `GPIO_Init` in our `gpio.cpp` file, so in the `include` folder we will create a `gpio.h` file to declare the function.

```c++
#ifndef GPIO_H__
#define GPIO_H__

void GPIO_Init(void);

#endif /* GPIO_H__ */
```

We have finished the `gpio.cpp` file. It would be a good time for a **_commit_** and **_push_**.

##### Development of `timer.cpp`

Create a file named `timer.cpp` in the `src` folder. In this file, **we will create two functions**: `TIMER_Init` and `startAdcConversion`. The first one will be used to **configure the _timer_**, and our teammate will call it from the `setup` function. The second function will be the **ISR that we execute every 100 ms**. We create both functions and configure _timer_ 3 to execute the `startAdcConversion` ISR every 100 ms. The code would look like this:

```c++
#include <Arduino.h>

void startAdcConversion(void);

void TIMER_Init(void)
{
    // Timer 3 configuration
    HardwareTimer *MyTim = new HardwareTimer(TIM3);

    MyTim->setMode(2, TIMER_OUTPUT_COMPARE);     // configure the timer mode with no output on any pin
    MyTim->setOverflow(100000, MICROSEC_FORMAT); // set the timer period to 100 ms
    MyTim->attachInterrupt(startAdcConversion);  // specify the ISR to be executed
    MyTim->resume();                             // start the timer
}

// Timer ISR
void startAdcConversion(void)
{
}
```

Finally, **in the ISR, we call the `conversionADC` function** that our teammate has implemented to perform an ADC conversion if it is enabled.

```c++
#include <Arduino.h>
#include "adc.h"

void startAdcConversion(void);

void TIMER_Init(void)
{
    // Timer 3 configuration
    HardwareTimer *MyTim = new HardwareTimer(TIM3);

    MyTim->setMode(2, TIMER_OUTPUT_COMPARE);     // configure the timer mode with no output on any pin
    MyTim->setOverflow(100000, MICROSEC_FORMAT); // set the timer period to 100 ms
    MyTim->attachInterrupt(startAdcConversion);  // specify the ISR to be executed
    MyTim->resume();                             // start the timer
}

// Timer ISR
void startAdcConversion(void)
{
    // try to start ADC conversion
    conversionADC();
}
```

We also need to create the `timer.h` file, which would contain the following:

```c++
#ifndef TIMER_H__
#define TIMER_H__

void TIMER_Init(void);

#endif /* TIMER_H__ */
```

With this, we would have the file finished. It’s the ideal moment for a **_commit_** and **_push_** of our changes.

##### _Pull Request_ and _Review_

Our work is almost finished. **Two things are still pending**. First, **create a _Pull Request_ from this branch to `arduino/develop` and, importantly, put our teammate `A` as the _reviewer_**. They will review our code, and if they approve it, either of you can perform the merge to the develop branch. If they do not approve it, you’ll need to address the requested changes, make the necessary modifications, commit and push the changes, and create a second review request.

I have added some tests to check that everything is ok before merging. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request, but **wait for your mate approval!**

Your work doesn’t end here because now **you will need to go to your teammate’s _Pull Request_, review that everything is ok**, and if so, approve their _Pull Request_. If you are not satisfied with their development, let them know and suggest changes. Once they apply the changes, approve their _Pull Request_ and either you or they will perform the merge to the `arduino/develop` branch.

Here is a [link](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/reviewing-changes-in-pull-requests) to GitHub’s help documentation where you can see in detail everything you can do during the _Pull Request_ review process.

> [!NOTE]
> In this project, it doesn’t matter who does the _merge_ to the `arduino/develop` branch first.

</details>

#### Summary

And with this, you’ve done your **first project together**! Have one team member create a Pull Request to the `main` branch. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request.

As you’ve seen, sometimes we call functions that are not ours, and whose names we shouldn’t initially know. **Git-based workflows**, or other tools, enable parallel development and collaboration on the same project. But **they don’t replace the essential team meetings** where **decisions are made** regarding the software architecture of a project, its directory structure, **how we’ll name the functions we implement**, etc. And typically, **all of this is documented** so it’s available to all team members.

## Evaluation

### Deliverables

These are the elements that should be available to the teacher for your evaluation:

- [ ] **Commits**
      Your remote GitHub repository must contain at least the following required commits: analog read, and analog serial.

- [ ] **Challenge**
      The challenge must be solved and included with its own commit.

- [ ] **Pull Requests**
      The different Pull Requests requested throughout the practice must also be present in your repository.

## Conclusions

In this practice, we’ve taken advantage of how **easy the ADC in Arduino is** (just use the `analogRead` function) to begin seeing how we can work on a **joint project** with our teammate. We’ve learned **how to develop in parallel** and how to **merge everything into one branch**. We’ve also seen how **git doesn’t replace the need for team meetings to agree on technical aspects of the project** that all development team members must follow. Finally, in this project, we saw how to **set a constant _sampling rate_**. This is crucial in ADC-based applications.

import java.util.Scanner;      //E_5_2

public class E5_2 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a number: ");
        double num = input.nextDouble();

        if (num == 0) {
            System.out.println("zero!");
        } else {
            if (num > 0)
                System.out.print("positive!");
            else
                System.out.print("negative!");

            double absNum = Math.abs(num);

            if (absNum < 1)
                System.out.print(" small!");
            else if (absNum > 1000000)
                System.out.print(" large!");

            System.out.println();
        }

        input.close();
    }
}

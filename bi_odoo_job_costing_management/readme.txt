
Version 12.0.0.2 :
	- Update create method of job order.
Version 12.0.0.4 :
	- Update report and in menu.
Version 12.0.0.5 :
1 add smart button in project issue and notes for project
2 hide button when stock count is zero.
3 set report layout for job orde, job cost sheet.
4 set product id form product.product instead of product.template.
5 fillup data in wizard project task form project issue.
6 update kanban now image is visible from image.
7 Add job_type_id domain for different job type for i.e material,labour,overhead in

Version 12.0.0.7 :
	-Solve issue while installation and of material requisition in v12.
	-Index Improvement with video.

version 12.0.0.8:
		 *purchase Requisition --> job costing sheet should be added 
               *Job order smart button is to be added in project template .
                *Purchase order smart button is to be added in project template.
               *Sub task is not linked with sub task smart button .
               *Task-->sub task tab should be remove (As in sub task smart button is present ) .
               *instead of purchase order line  ,purchase order  should be linked with purchase order smart button 
               *Instead of vendor bill line ,vendor bill should be linked with vendor bill smart button .
                *Requisition menu item should be remove .
                *Internal picking sequence is same to cost sheet sequence .

Date 17th march 2020
version 12.0.0.9
  - -->Job order and job cost sheet should be linked and once job order has been selected the planning material should be fetched in the job cost sheet .
  -->vendors field should be required field for the purchase order not for the internal picking in “material requisition”
  -->job type field should be added in job order
  -->job cost sheet-->material tab-->material should be selected automatically and should be read only
  -->job cost sheet-->overhead tab-->overhead should be selected automatically and should be read only
  -->job cost sheet-->labour tab-->labour should be selected automatically and should be read only
  -->purchase requisition-->received date field should be non editable .


Date 26th march 2020
version 12.0.1.0
issue and improvement:-
  --> Job cost sheet the product are fetched multiple time  when we click the job order
  --> In Purchase order "Job order" name should be changed to "job cost sheet" and the cost sheet name should be fetched from the purchase requisition .. 
  --> In Internal Picking and incoming shipment  form view  change the name of the "Job Material requisition"to job order
  --> Actual Purchase and Actual Invoice quantity not get properly
  -->  actual requisition qty update when material requisition generate
  --> update fields name
  --> Cost unit should be fetched from the product template(NOT IMPROVED)
  --> Job Notes is been Duplicate once the we change the stage of the previous Job Note
  --> Actual Purchase and Actual Invoice quantity quantity should be reflected not the price 
  --> Job cost sheet the product are fetched multiple time  when we click the job order 
  --> Job Order should also be fetched from the costsheet to purchase requisition
  --> cost sheet should be selected automatically in purchase order and vendor bill (if in the purchase requisition cost sheet is selected )
  --> Total Cost =Total cost (Cost sheet 1)+Total cost (Cost sheet 2)+...Total cost (Cost sheet n)
  --> Total Cost of Project should be display in the project
  --> Cost unit should be fetched from the product template
  --> In Labour tab only service product should be selected
  --> job order select job type is labour its filter with serviceable product
  --> actual quantity and invoice quantity generate error while multiple job cost sheet added.


#include <Python.h>


extern int lectur_(int *, char *, int *, int *,int *, float *, float*, int *, int *, int *, float *, float *, int *, float *, float *,float *, float *,float *, int *, char *, int *);
extern int dimens_(int *, char *, int *, int *, int *);
extern int ertxt_(int *);


static PyObject *
tjiidata_dimens(PyObject *self, PyObject *args)
{
  int error,ndes;
  char *senal;
  if (!PyArg_ParseTuple(args, "is", &ndes, &senal))
    return NULL;

  int ierr, ndat, nvent, status;

  status=dimens_(&ndes, senal, &ndat, &nvent, &ierr);
  if (ierr) {
    printf("dimens returned error. No exception handling (or garbage collection) yet...");
    return NULL;
  }
  return Py_BuildValue("(l,l)", ndat,nvent);
  
}

static PyObject * 
tjiidata_lectur(PyObject *self, PyObject *args)
{
  
  
  int error;

  char *senal, unidad[32];

  int ndes, ndimv, ndimx, ndimy;
    

  if (!PyArg_ParseTuple(args, "isiii", &ndes, &senal, &ndimx, &ndimy, &ndimv))
    return NULL;


  int code0, ierr, mv[ndimv], nbits, ndat, nvent, status, i,j,k;
  float factor, offset, per[ndimv], tini[ndimv], vpp, x[ndimx], y[ndimy], ymax, ymin;


  errno = 0;
  status = lectur_(&ndes, senal, &ndimx, &ndimy, &ndimv, x, y, &ndat, &nvent, mv, per, tini, &nbits, &offset, &ymax, &ymin, &factor, &vpp, &code0, unidad, &ierr);

  if (ierr) {
    printf("dimens returned error. No exception handling (or garbage collection) yet...");
    return NULL;
  }

  /* hack: there are  more efficient ways to return an array... */

  PyObject *XList=PyList_New(ndimx);
  
  for (i = 0; i < ndimx; i++) {
    PyObject *op = PyFloat_FromDouble((double)x[i]);
    if (PyList_SetItem(XList,i,op) !=0) {
      fprintf(stderr,"Error in creating python XList object\n");
      exit(EXIT_FAILURE);
    }
  } 
  PyObject *YList=PyList_New(ndimy);
  
  for (i = 0; i < ndimy; i++) {
    PyObject *op = PyFloat_FromDouble((double)y[i]);
    if (PyList_SetItem(YList,i,op) !=0) {
      fprintf(stderr,"Error in creating python YList object\n");
      exit(EXIT_FAILURE);
    }
  } 
  PyObject *MVList=PyList_New(ndimv);
  
  for (i = 0; i < ndimv; i++) {
    PyObject *op = PyFloat_FromDouble((double)mv[i]);
    if (PyList_SetItem(MVList,i,op) !=0) {
      fprintf(stderr,"Error in creating python MVList object\n");
      exit(EXIT_FAILURE);
    }
  } 

  PyObject *PERList=PyList_New(ndimv);
  
  for (i = 0; i < ndimv; i++) {
    PyObject *op = PyFloat_FromDouble((double)per[i]);
    if (PyList_SetItem(PERList,i,op) !=0) {
      fprintf(stderr,"Error in creating python PERList object\n");
      exit(EXIT_FAILURE);
    }
  } 
  PyObject *TINIList=PyList_New(ndimv);
  
  for (i = 0; i < ndimv; i++) {
    PyObject *op = PyFloat_FromDouble((double)tini[i]);
    if (PyList_SetItem(TINIList,i,op) !=0) {
      fprintf(stderr,"Error in creating python XList object\n");
      exit(EXIT_FAILURE);
    }
  } 

  
  return Py_BuildValue("{s:i,s:s,s:l,s:l,s:l,s:N,s:N,s:i,s:i,s:N,s:n,s:N,s:i,s:f,s:f,s:f,s:f,s:f,s:i,s:s,s:i}", "ndes", ndes, "senal",senal,"ndimx",ndimx, "ndimy",ndimy, "ndimv",ndimv,"x",XList, "y",YList, "ndat", ndat, "nvent", nvent,"mv",MVList,"per",PERList,"tini",TINIList,"nbits",nbits,"offset",offset,"ymax",ymax,"ymin",ymin,"factor",factor,"vpp",vpp,"code0",code0,"unidad",unidad,"ierr",ierr);


}


static PyMethodDef tjiidata_methods[] = {
    /* The cast of the function is necessary since PyCFunction values
     * only take two PyObject* parameters, and keywdarg_parrot() takes
     * three.
     */
    {"lectur", (PyCFunction)tjiidata_lectur, METH_VARARGS | METH_KEYWORDS,
     "Load data...."},
    {"dimens", (PyCFunction)tjiidata_dimens, METH_VARARGS | METH_KEYWORDS,
     "Get data dimens...."},
    {NULL, NULL, 0, NULL}   /* sentinel */
};

void
inittjiidata(void)
{
  /* Create the module and add the functions */
  Py_InitModule("tjiidata", tjiidata_methods);
}

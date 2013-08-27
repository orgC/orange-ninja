#ifndef ATS_WALK_H
#define ATS_WALK_H

#define BUF_SIZE 256 //
#define LIST_LEN 10000 // record 1000 file in one list
#define MAX_NODE_NO LIST_LEN-1

#define GCOV_LIST_NO 	10
#define GCOV_MAX_LINE_NO 	10000 // assume the max line number of one source file is 10K

#define CRASH_HERE(x...) \
	do { \
		char __buf[512];\
		sprintf(__buf,x);\
		printf("[CRASH %s@%s:%d] %s", __FUNCTION__, __FILE__, __LINE__, __buf); \
		*(int*)0 = 1; \
	} while(0)

static int gcov_count = 0;



typedef struct _name_info {
	char name[BUF_SIZE];
}name_info;

typedef struct _list_info {
	int count;
	int max;
	name_info *node;
}list_info;

typedef struct _cover_record {
	
	int run_no;
	int line;
}cover_record;

typedef struct _gcov_file_info {
	char filename[256];
	char path[512];
	int  count;
	cover_record *cover_head;
}gcov_file_info;

typedef struct 
{
	int load_id;
	char load_name[256];
	int case_id;
	char case_name[256];
	int src_id;
	char src_name[256];
	
}db_load_info;

typedef struct _param_t
{
	name_info *p_node;
	int length;
	int no;
	db_load_info *db_info;
}param_t;




#endif


